using System.Collections.Generic;

namespace ReelScope.App.Models
{
    public class SegmentAnalysisResponse
    {
        public int K { get; set; }
        public double SilhouetteScore { get; set; }
        public int RandomState { get; set; }
        public List<ClusterProfile> Clusters { get; set; } = new();
        public List<FeatureImportanceItem> FeatureImportance { get; set; } = new();
        public List<ClusterScatterPoint> Scatter { get; set; } = new();
        public RadarData? Radar { get; set; }
    }

    public class ClusterProfile
    {
        public int ClusterId { get; set; }
        public string Name { get; set; } = string.Empty;
        public int ItemsCount { get; set; }
        public double PctOfTotal { get; set; }
        public double AvgViews24h { get; set; }
        public double AvgEngagementRate { get; set; }
        public double AvgSaveRate { get; set; }
        public double AvgCompletionRate { get; set; }
        public double AvgVelocity24h { get; set; }
        public double AvgDurationSec { get; set; }
        public double AvgGrowthRatio7d { get; set; }
    }

    public class FeatureImportanceItem
    {
        public string Feature { get; set; } = string.Empty;
        public double Weight { get; set; }
    }

    public class ClusterScatterPoint
    {
        public string PostId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public long Views { get; set; }
        public double EngagementRate { get; set; }
        public int Cluster { get; set; }
    }

    public class RadarData
    {
        public List<string> Dimensions { get; set; } = new();
        public List<RadarSeriesItem> Series { get; set; } = new();
    }

    public class RadarSeriesItem
    {
        public string Name { get; set; } = string.Empty;
        public List<double> Values { get; set; } = new();
    }

    public class AnomalyItem
    {
        public string PostId { get; set; } = string.Empty;
        public string Platform { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Metric { get; set; } = string.Empty;
        public double ActualValue { get; set; }
        public double ExpectedMedian { get; set; }
        public double RobustZ { get; set; }
        public string Direction { get; set; } = string.Empty;
        public string Method { get; set; } = string.Empty;
    }
}
