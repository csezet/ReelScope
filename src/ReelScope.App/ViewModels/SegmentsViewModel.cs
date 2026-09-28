using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using ReelScope.App.Models;
using ReelScope.App.Services;

namespace ReelScope.App.ViewModels
{
    public class SegmentsViewModel : ViewModelBase
    {
        private readonly ApiClient _api;
        private bool _isLoading;
        private int _k = 4;
        private double _silhouetteScore;
        private ClusterProfile? _selectedCluster;

        public bool IsLoading { get => _isLoading; set => SetField(ref _isLoading, value); }
        public int K { get => _k; set => SetField(ref _k, value); }
        public double SilhouetteScore { get => _silhouetteScore; set => SetField(ref _silhouetteScore, value); }

        public ClusterProfile? SelectedCluster
        {
            get => _selectedCluster;
            set => SetField(ref _selectedCluster, value);
        }

        public ObservableCollection<ClusterProfile> Clusters { get; } = new();
        public ObservableCollection<FeatureImportanceItem> FeatureImportance { get; } = new();
        public ObservableCollection<ClusterScatterPoint> ScatterPoints { get; } = new();
        public ObservableCollection<AnomalyItem> Anomalies { get; } = new();
        public RadarData? Radar { get; private set; }

        public SegmentsViewModel(ApiClient api)
        {
            _api = api;
        }

        public async Task RunAnalysisAsync(CancellationToken ct = default)
        {
            IsLoading = true;
            try
            {
                var payload = new { k = K, random_state = 42 };
                var resp = await _api.PostAsync<object, SegmentAnalysisResponse>("/api/segments/run", payload, ct);

                if (resp != null)
                {
                    SilhouetteScore = resp.SilhouetteScore;
                    Radar = resp.Radar;

                    Clusters.Clear();
                    resp.Clusters?.ForEach(Clusters.Add);

                    if (Clusters.Count > 0)
                        SelectedCluster = Clusters[0];

                    FeatureImportance.Clear();
                    resp.FeatureImportance?.ForEach(FeatureImportance.Add);

                    ScatterPoints.Clear();
                    resp.Scatter?.ForEach(ScatterPoints.Add);
                }

                // Load anomalies
                var anomaliesList = await _api.GetAsync<List<AnomalyItem>>("/api/segments/anomalies", ct);
                Anomalies.Clear();
                anomaliesList?.ForEach(Anomalies.Add);
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
