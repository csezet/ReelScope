using System.IO;
using System.Threading.Tasks;
using ReelScope.App.Services;

namespace ReelScope.App.ViewModels
{
    public class SettingsViewModel : ViewModelBase
    {
        private readonly ApiClient _api;
        private string _databasePath = string.Empty;
        private string _engineStatus = "Connecting...";
        private string _pythonVersion = "Unknown";
        private string _duckDbVersion = "Unknown";
        private double _acrylicBlurStrength = 80.0;
        private bool _accentGlowEnabled = true;

        public string DatabasePath { get => _databasePath; set => SetField(ref _databasePath, value); }
        public string EngineStatus { get => _engineStatus; set => SetField(ref _engineStatus, value); }
        public string PythonVersion { get => _pythonVersion; set => SetField(ref _pythonVersion, value); }
        public string DuckDbVersion { get => _duckDbVersion; set => SetField(ref _duckDbVersion, value); }
        public double AcrylicBlurStrength { get => _acrylicBlurStrength; set => SetField(ref _acrylicBlurStrength, value); }
        public bool AccentGlowEnabled { get => _accentGlowEnabled; set => SetField(ref _accentGlowEnabled, value); }

        public SettingsViewModel(ApiClient api)
        {
            _api = api;
            DatabasePath = Path.Combine(
                System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData),
                "ReelScope", "data", "reelscope.duckdb"
            );
        }

        public async Task RefreshStatusAsync()
        {
            try
            {
                var health = await _api.GetAsync<System.Text.Json.JsonElement>("/health");
                if (health.ValueKind != System.Text.Json.JsonValueKind.Undefined)
                {
                    EngineStatus = "Running";
                    if (health.TryGetProperty("python_version", out var py))
                        PythonVersion = py.GetString() ?? "3.12+";
                    if (health.TryGetProperty("duckdb_version", out var ddb))
                        DuckDbVersion = ddb.GetString() ?? "0.10+";
                }
            }
            catch
            {
                EngineStatus = "Offline / Error";
            }
        }

        public async Task ResetDatabaseAsync()
        {
            await _api.PostAsync<object>("/api/demo/reset");
        }
    }
}
