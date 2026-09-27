using System;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using ReelScope.App.Models;
using ReelScope.App.Services;

namespace ReelScope.App.ViewModels
{
    public class OverviewViewModel : ViewModelBase
    {
        private readonly ApiClient _api;
        private bool _isLoading;
        private bool _hasData;
        private string? _selectedPlatform = "All";
        private int _selectedDays = 28;

        // KPI Properties
        private long _totalViews;
        private double _viewsLift;
        private double _engagementRate;
        private double _engagementLift;
        private double _completionRate;
        private double _completionLift;
        private long _saves;
        private double _savesLift;
        private long _followersGained;
        private double _followersLift;

        public bool IsLoading
        {
            get => _isLoading;
            set => SetField(ref _isLoading, value);
        }

        public bool HasData
        {
            get => _hasData;
            set => SetField(ref _hasData, value);
        }

        public string? SelectedPlatform
        {
            get => _selectedPlatform;
            set
            {
                if (SetField(ref _selectedPlatform, value))
                {
                    _ = LoadDataAsync();
                }
            }
        }

        public int SelectedDays
        {
            get => _selectedDays;
            set
            {
                if (SetField(ref _selectedDays, value))
                {
                    _ = LoadDataAsync();
                }
            }
        }

        public long TotalViews { get => _totalViews; set => SetField(ref _totalViews, value); }
        public double ViewsLift { get => _viewsLift; set => SetField(ref _viewsLift, value); }
        public double EngagementRate { get => _engagementRate; set => SetField(ref _engagementRate, value); }
        public double EngagementLift { get => _engagementLift; set => SetField(ref _engagementLift, value); }
        public double CompletionRate { get => _completionRate; set => SetField(ref _completionRate, value); }
        public double CompletionLift { get => _completionLift; set => SetField(ref _completionLift, value); }
        public long Saves { get => _saves; set => SetField(ref _saves, value); }
        public double SavesLift { get => _savesLift; set => SetField(ref _savesLift, value); }
        public long FollowersGained { get => _followersGained; set => SetField(ref _followersGained, value); }
        public double FollowersLift { get => _followersLift; set => SetField(ref _followersLift, value); }

        public ObservableCollection<PlatformMixItem> PlatformMix { get; } = new();
        public ObservableCollection<FormatBreakdownItem> FormatBreakdown { get; } = new();
        public ObservableCollection<RecentPostItem> RecentPosts { get; } = new();
        public ObservableCollection<InsightItem> Insights { get; } = new();
        public ObservableCollection<PerformancePoint> PerformanceSeries { get; } = new();

        public OverviewViewModel(ApiClient api)
        {
            _api = api;
        }

        public async Task LoadDataAsync(CancellationToken ct = default)
        {
            IsLoading = true;
            try
            {
                string platParam = string.IsNullOrEmpty(SelectedPlatform) || SelectedPlatform == "All" ? "" : $"&platform={SelectedPlatform.ToLowerInvariant()}";
                string url = $"/api/dashboard?days={SelectedDays}{platParam}";

                var data = await _api.GetAsync<DashboardResponse>(url, ct);
                if (data != null && data.HasData)
                {
                    HasData = true;

                    if (data.Kpis != null)
                    {
                        if (data.Kpis.TryGetValue("views", out var v))
                        {
                            TotalViews = (long)(v.Value ?? 0);
                            ViewsLift = v.LiftPct ?? 0;
                        }
                        if (data.Kpis.TryGetValue("engagement_rate", out var e))
                        {
                            EngagementRate = e.Value ?? 0;
                            EngagementLift = e.LiftPct ?? 0;
                        }
                        if (data.Kpis.TryGetValue("completion_rate", out var c))
                        {
                            CompletionRate = c.Value ?? 0;
                            CompletionLift = c.LiftPct ?? 0;
                        }
                        if (data.Kpis.TryGetValue("saves", out var s))
                        {
                            Saves = (long)(s.Value ?? 0);
                            SavesLift = s.LiftPct ?? 0;
                        }
                        if (data.Kpis.TryGetValue("followers_gained", out var f))
                        {
                            FollowersGained = (long)(f.Value ?? 0);
                            FollowersLift = f.LiftPct ?? 0;
                        }
                    }

                    PlatformMix.Clear();
                    data.PlatformMix?.ForEach(PlatformMix.Add);

                    FormatBreakdown.Clear();
                    data.FormatBreakdown?.ForEach(FormatBreakdown.Add);

                    RecentPosts.Clear();
                    data.RecentPosts?.ForEach(RecentPosts.Add);

                    Insights.Clear();
                    data.Insights?.ForEach(Insights.Add);

                    PerformanceSeries.Clear();
                    data.PerformanceSeries?.ForEach(PerformanceSeries.Add);
                }
                else
                {
                    HasData = false;
                }
            }
            finally
            {
                IsLoading = false;
            }
        }

        public async Task LoadDemoDatasetAsync()
        {
            IsLoading = true;
            try
            {
                await _api.PostAsync<object>("/api/demo/load");
                await LoadDataAsync();
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
