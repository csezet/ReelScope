using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using ReelScope.App.Models;
using ReelScope.App.Services;

namespace ReelScope.App.ViewModels
{
    public class CohortsViewModel : ViewModelBase
    {
        private readonly ApiClient _api;
        private bool _isLoading;
        private string _selectedMetric = "views";
        private string? _selectedPlatform = "All";
        private string _avg7dRetention = "28.4%";
        private string _avg30dEngagement = "6.2%";
        private string _avg30dSaves = "4.8%";
        private string _cohortFollowerGrowth = "+12.6K";

        public bool IsLoading { get => _isLoading; set => SetField(ref _isLoading, value); }

        public string SelectedMetric
        {
            get => _selectedMetric;
            set
            {
                if (SetField(ref _selectedMetric, value))
                    _ = LoadCohortsAsync();
            }
        }

        public string? SelectedPlatform
        {
            get => _selectedPlatform;
            set
            {
                if (SetField(ref _selectedPlatform, value))
                    _ = LoadCohortsAsync();
            }
        }

        public string Avg7dRetention { get => _avg7dRetention; set => SetField(ref _avg7dRetention, value); }
        public string Avg30dEngagement { get => _avg30dEngagement; set => SetField(ref _avg30dEngagement, value); }
        public string Avg30dSaves { get => _avg30dSaves; set => SetField(ref _avg30dSaves, value); }
        public string CohortFollowerGrowth { get => _cohortFollowerGrowth; set => SetField(ref _cohortFollowerGrowth, value); }

        public ObservableCollection<CohortRow> Rows { get; } = new();
        public ObservableCollection<InsightItem> Insights { get; } = new();

        public CohortsViewModel(ApiClient api)
        {
            _api = api;
        }

        public async Task LoadCohortsAsync(CancellationToken ct = default)
        {
            IsLoading = true;
            try
            {
                var payload = new
                {
                    metric = SelectedMetric.ToLowerInvariant(),
                    platform = (string.IsNullOrEmpty(SelectedPlatform) || SelectedPlatform == "All") ? null : SelectedPlatform.ToLowerInvariant()
                };

                var resp = await _api.PostAsync<object, CohortResponse>("/api/cohorts/query", payload, ct);
                if (resp != null)
                {
                    Rows.Clear();
                    resp.Matrix?.Rows?.ForEach(Rows.Add);

                    Insights.Clear();
                    resp.Insights?.ForEach(Insights.Add);
                }
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
