using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace ReelScope.App.Services
{
    public class ApiClient
    {
        private readonly HttpClient _http;
        private readonly EngineProcessService _engineService;
        private static readonly JsonSerializerOptions _jsonOpts = new()
        {
            PropertyNameCaseInsensitive = true
        };

        public ApiClient(EngineProcessService engineService)
        {
            _engineService = engineService;
            _http = new HttpClient();
        }

        private HttpRequestMessage CreateRequest(HttpMethod method, string path)
        {
            var req = new HttpRequestMessage(method, $"{_engineService.BaseUrl}{path}");
            if (!string.IsNullOrEmpty(_engineService.SessionToken))
            {
                req.Headers.Add("X-ReelScope-Token", _engineService.SessionToken);
            }
            return req;
        }

        public async Task<T?> GetAsync<T>(string path, CancellationToken ct = default)
        {
            using var req = CreateRequest(HttpMethod.Get, path);
            using var resp = await _http.SendAsync(req, ct);
            resp.EnsureSuccessStatusCode();
            var stream = await resp.Content.ReadAsStreamAsync(ct);
            return await JsonSerializer.DeserializeAsync<T>(stream, _jsonOpts, ct);
        }

        public async Task<TOut?> PostAsync<TIn, TOut>(string path, TIn payload, CancellationToken ct = default)
        {
            using var req = CreateRequest(HttpMethod.Post, path);
            string json = JsonSerializer.Serialize(payload, _jsonOpts);
            req.Content = new StringContent(json, Encoding.UTF8, "application/json");

            using var resp = await _http.SendAsync(req, ct);
            resp.EnsureSuccessStatusCode();
            var stream = await resp.Content.ReadAsStreamAsync(ct);
            return await JsonSerializer.DeserializeAsync<TOut>(stream, _jsonOpts, ct);
        }

        public async Task<TOut?> PostAsync<TOut>(string path, CancellationToken ct = default)
        {
            using var req = CreateRequest(HttpMethod.Post, path);
            using var resp = await _http.SendAsync(req, ct);
            resp.EnsureSuccessStatusCode();
            var stream = await resp.Content.ReadAsStreamAsync(ct);
            return await JsonSerializer.DeserializeAsync<TOut>(stream, _jsonOpts, ct);
        }
    }
}
