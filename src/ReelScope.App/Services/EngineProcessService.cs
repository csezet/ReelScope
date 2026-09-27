using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace ReelScope.App.Services
{
    public class EngineProcessService : IDisposable
    {
        private Process? _engineProcess;
        private readonly HttpClient _httpClient;
        
        public int Port { get; private set; }
        public string SessionToken { get; private set; } = string.Empty;
        public string BaseUrl => $"http://127.0.0.1:{Port}";
        public bool IsRunning => _engineProcess != null && !_engineProcess.HasExited;

        public EngineProcessService()
        {
            _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
        }

        public static int GetAvailablePort()
        {
            using var listener = new TcpListener(IPAddress.Loopback, 0);
            listener.Start();
            int port = ((IPEndPoint)listener.LocalEndpoint).Port;
            listener.Stop();
            return port;
        }

        public static string GenerateSessionToken()
        {
            byte[] bytes = new byte[32];
            using var rng = RandomNumberGenerator.Create();
            rng.GetBytes(bytes);
            return Convert.ToHexString(bytes).ToLowerInvariant();
        }

        public async Task StartAsync(string? enginePath = null, CancellationToken ct = default)
        {
            Port = GetAvailablePort();
            SessionToken = GenerateSessionToken();

            string dataDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "ReelScope", "data"
            );
            Directory.CreateDirectory(dataDir);

            ProcessStartInfo psi;

            // In production: packaged reelscope-engine.exe
            // In dev mode: run through python venv
            if (!string.IsNullOrEmpty(enginePath) && File.Exists(enginePath))
            {
                psi = new ProcessStartInfo
                {
                    FileName = enginePath,
                    Arguments = $"--host 127.0.0.1 --port {Port}",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                };
            }
            else
            {
                // Fallback to local .venv python in development
                string projectRoot = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", ".."));
                string venvPython = Path.Combine(projectRoot, ".venv", "Scripts", "python.exe");

                if (!File.Exists(venvPython))
                {
                    venvPython = "python"; // fallback to system PATH
                }

                psi = new ProcessStartInfo
                {
                    FileName = venvPython,
                    Arguments = $"-m reelscope_engine --host 127.0.0.1 --port {Port}",
                    WorkingDirectory = projectRoot,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                };
            }

            // Secure token and data dir passed strictly via environment variables
            psi.Environment["REELSCOPE_TOKEN"] = SessionToken;
            psi.Environment["REELSCOPE_DATA_DIR"] = dataDir;

            _engineProcess = Process.Start(psi) 
                ?? throw new InvalidOperationException("Failed to spawn ReelScope analytics engine process.");

            // Poll /health endpoint until engine reports ready state
            using var timeoutCts = new CancellationTokenSource(TimeSpan.FromSeconds(20));
            using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(ct, timeoutCts.Token);

            while (!linkedCts.IsCancellationRequested)
            {
                try
                {
                    var response = await _httpClient.GetAsync($"{BaseUrl}/health", linkedCts.Token);
                    if (response.IsSuccessStatusCode)
                    {
                        string body = await response.Content.ReadAsStringAsync(linkedCts.Token);
                        using var doc = JsonDocument.Parse(body);
                        if (doc.RootElement.GetProperty("status").GetString() == "ready")
                        {
                            return; // Engine ready!
                        }
                    }
                }
                catch
                {
                    // Engine still booting
                }

                if (_engineProcess.HasExited)
                {
                    string stderr = await _engineProcess.StandardError.ReadToEndAsync(ct);
                    throw new InvalidOperationException($"Engine crashed prematurely with exit code {_engineProcess.ExitCode}: {stderr}");
                }

                await Task.Delay(250, linkedCts.Token);
            }

            throw new TimeoutException("Analytics engine health check timed out after 20 seconds.");
        }

        public async Task StopAsync()
        {
            if (_engineProcess == null || _engineProcess.HasExited) return;

            try
            {
                // Request graceful shutdown via API
                var req = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/shutdown");
                req.Headers.Add("X-ReelScope-Token", SessionToken);
                await _httpClient.SendAsync(req);

                // Wait up to 3 seconds for exit
                await Task.Run(() => _engineProcess.WaitForExit(3000));
            }
            catch
            {
                // Fallback to force kill if unresponsive
            }
            finally
            {
                if (!_engineProcess.HasExited)
                {
                    _engineProcess.Kill(entireProcessTree: true);
                }
                _engineProcess.Dispose();
                _engineProcess = null;
            }
        }

        public void Dispose()
        {
            StopAsync().GetAwaiter().GetResult();
            _httpClient.Dispose();
        }
    }
}
