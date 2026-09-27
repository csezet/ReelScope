using System.Collections.Generic;

namespace ReelScope.App.Models
{
    // Cohorts
    public class CohortResponse
    {
        public Dictionary<string, object>? Kpis { get; set; }
        public CohortMatrix? Matrix { get; set; }
        public List<InsightItem>? Insights { get; set; }
    }

    public class CohortMatrix
    {
        public string Metric { get; set; } = string.Empty;
        public List<int> Checkpoints { get; set; } = new();
        public List<CohortRow> Rows { get; set; } = new();
    }

    public class CohortRow
    {
        public string CohortMonth { get; set; } = string.Empty;
        public int PostsCount { get; set; }
        public Dictionary<string, double?> Values { get; set; } = new();
        public Dictionary<string, double?> Retention { get; set; } = new();
    }

    // Experiments
    public class ExperimentAnalysisResponse
    {
        public Dictionary<string, object>? Experiment { get; set; }
        public VariantSummary? ControlSummary { get; set; }
        public VariantSummary? TreatmentSummary { get; set; }
        public Dictionary<string, object>? StatisticalResults { get; set; }
        public BootstrapData? Bootstrap { get; set; }
        public List<TimelinePoint>? TimelineSeries { get; set; }
        public List<string>? Recommendations { get; set; }
    }

    public class VariantSummary
    {
        public string Label { get; set; } = string.Empty;
        public int SampleSize { get; set; }
        public double ConversionRate { get; set; }
        public double CompletionRate { get; set; }
    }

    public class BootstrapData
    {
        public double ObservedLift { get; set; }
        public double CiLower95 { get; set; }
        public double CiUpper95 { get; set; }
        public HistogramData? Histogram { get; set; }
    }

    public class HistogramData
    {
        public List<double> Bins { get; set; } = new();
        public List<int> Counts { get; set; } = new();
    }

    public class TimelinePoint
    {
        public string Day { get; set; } = string.Empty;
        public double Control { get; set; }
        public double Treatment { get; set; }
    }
}
