using System.Collections.Generic;

namespace ReelScope.App.Models
{
    public class DashboardResponse
    {
        public bool HasData { get; set; }
        public string? Message { get; set; }
        public Dictionary<string, KpiMetric>? Kpis { get; set; }
        public List<PerformancePoint>? PerformanceSeries { get; set; }
        public List<PlatformMixItem>? PlatformMix { get; set; }
        public List<FormatBreakdownItem>? FormatBreakdown { get; set; }
        public List<RecentPostItem>? RecentPosts { get; set; }
        public List<InsightItem>? Insights { get; set; }
    }

    public class KpiMetric
    {
        public double? Value { get; set; }
        public double? LiftPct { get; set; }
        public List<double>? Sparkline { get; set; }
    }

    public class PerformancePoint
    {
        public string? DateStr { get; set; }
        public int DailyPosts { get; set; }
        public long DailyViews { get; set; }
        public long DailyEng { get; set; }
        public double? DailyCr { get; set; }
    }

    public class PlatformMixItem
    {
        public string? Platform { get; set; }
        public int Posts { get; set; }
        public long Views { get; set; }
        public double SharePct { get; set; }
    }

    public class FormatBreakdownItem
    {
        public string? Format { get; set; }
        public int Posts { get; set; }
        public long Views { get; set; }
        public double EngRate { get; set; }
    }

    public class RecentPostItem
    {
        public string? PostId { get; set; }
        public string? Platform { get; set; }
        public string? Title { get; set; }
        public string? PublishedAt { get; set; }
        public long Views { get; set; }
        public double EngRate { get; set; }
        public string? ThumbnailUrl { get; set; }
    }

    public class InsightItem
    {
        public string? Type { get; set; }
        public string? Title { get; set; }
        public string? Description { get; set; }
    }
}
