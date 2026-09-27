using System.Collections.ObjectModel;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using ReelScope.App.Models;
using ReelScope.App.Services;

namespace ReelScope.App.ViewModels
{
    public class ExperimentsViewModel : ViewModelBase
    {
        private readonly ApiClient _api;
        private bool _isLoading;
        private string _selectedExperimentId = "exp_hook_length";

        private string _controlTitle = "Standard Hook (3s)";
        private int _controlSampleSize = 1500;
        private double _controlRate = 42.1;
        private double _controlCompletionRate = 72.0;

        private string _treatmentTitle = "Fast Punchy Hook (1.5s)";
        private int _treatmentSampleSize = 1500;
        private double _treatmentRate = 46.8;
        private double _treatmentCompletionRate = 76.0;

        private string _absoluteLift = "+4.7 pp";
        private string _relativeLift = "+11.2%";
        private string _confidenceInterval = "+1.8% to +7.6%";
        private string _pValue = "0.0031";
        private bool _isSignificant = true;

        public bool IsLoading { get => _isLoading; set => SetField(ref _isLoading, value); }

        public string SelectedExperimentId
        {
            get => _selectedExperimentId;
            set
            {
                if (SetField(ref _selectedExperimentId, value))
                    _ = RunAnalysisAsync();
            }
        }

        public string ControlTitle { get => _controlTitle; set => SetField(ref _controlTitle, value); }
        public int ControlSampleSize { get => _controlSampleSize; set => SetField(ref _controlSampleSize, value); }
        public double ControlRate { get => _controlRate; set => SetField(ref _controlRate, value); }
        public double ControlCompletionRate { get => _controlCompletionRate; set => SetField(ref _controlCompletionRate, value); }

        public string TreatmentTitle { get => _treatmentTitle; set => SetField(ref _treatmentTitle, value); }
        public int TreatmentSampleSize { get => _treatmentSampleSize; set => SetField(ref _treatmentSampleSize, value); }
        public double TreatmentRate { get => _treatmentRate; set => SetField(ref _treatmentRate, value); }
        public double TreatmentCompletionRate { get => _treatmentCompletionRate; set => SetField(ref _treatmentCompletionRate, value); }

        public string AbsoluteLift { get => _absoluteLift; set => SetField(ref _absoluteLift, value); }
        public string RelativeLift { get => _relativeLift; set => SetField(ref _relativeLift, value); }
        public string ConfidenceInterval { get => _confidenceInterval; set => SetField(ref _confidenceInterval, value); }
        public string PValue { get => _pValue; set => SetField(ref _pValue, value); }
        public bool IsSignificant { get => _isSignificant; set => SetField(ref _isSignificant, value); }

        public ObservableCollection<TimelinePoint> TimelineSeries { get; } = new();
        public ObservableCollection<string> Recommendations { get; } = new();
        public BootstrapData? Bootstrap { get; private set; }

        public ExperimentsViewModel(ApiClient api)
        {
            _api = api;
        }

        public async Task RunAnalysisAsync(CancellationToken ct = default)
        {
            IsLoading = true;
            try
            {
                var payload = new
                {
                    experiment_id = SelectedExperimentId,
                    alpha = 0.05,
                    n_bootstrap = 10000
                };

                var resp = await _api.PostAsync<object, ExperimentAnalysisResponse>("/api/experiments/analyze", payload, ct);
                if (resp != null)
                {
                    if (resp.ControlSummary != null)
                    {
                        ControlTitle = resp.ControlSummary.Label;
                        ControlSampleSize = resp.ControlSummary.SampleSize;
                        ControlRate = resp.ControlSummary.ConversionRate;
                        ControlCompletionRate = resp.ControlSummary.CompletionRate;
                    }

                    if (resp.TreatmentSummary != null)
                    {
                        TreatmentTitle = resp.TreatmentSummary.Label;
                        TreatmentSampleSize = resp.TreatmentSummary.SampleSize;
                        TreatmentRate = resp.TreatmentSummary.ConversionRate;
                        TreatmentCompletionRate = resp.TreatmentSummary.CompletionRate;
                    }

                    if (resp.StatisticalResults != null)
                    {
                        if (resp.StatisticalResults.TryGetValue("absolute_lift_pp", out var absVal))
                            AbsoluteLift = $"+{absVal} pp";
                        if (resp.StatisticalResults.TryGetValue("relative_lift_pct", out var relVal))
                            RelativeLift = $"+{relVal}%";
                        if (resp.StatisticalResults.TryGetValue("ci_lower_pp", out var cLo) && resp.StatisticalResults.TryGetValue("ci_upper_pp", out var cHi))
                            ConfidenceInterval = $"{cLo}% to {cHi}%";
                        if (resp.StatisticalResults.TryGetValue("p_value", out var pv))
                            PValue = pv.ToString() ?? "0.0";
                        if (resp.StatisticalResults.TryGetValue("is_significant", out var sig))
                            IsSignificant = sig is JsonElement je ? je.GetBoolean() : (bool)sig;
                    }

                    Bootstrap = resp.Bootstrap;

                    TimelineSeries.Clear();
                    resp.TimelineSeries?.ForEach(TimelineSeries.Add);

                    Recommendations.Clear();
                    resp.Recommendations?.ForEach(Recommendations.Add);
                }
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
