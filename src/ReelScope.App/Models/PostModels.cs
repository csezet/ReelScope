using System.Collections.Generic;

namespace ReelScope.App.Models
{
    public class PostListResponse
    {
        public int Total { get; set; }
        public int Limit { get; set; }
        public int Offset { get; set; }
        public List<PostItem> Posts { get; set; } = new();
        public List<ScatterPoint> Scatter { get; set; } = new();
    }

    public class PostItem
    {
        public string PostId { get; set; } = string.Empty;
        public string Platform { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string PublishedAt { get; set; } = string.Empty;
        public double DurationSec { get; set; }
        public string ContentType { get; set; } = string.Empty;
        public string Tags { get; set; } = string.Empty;
        public string ThumbnailUrl { get; set; } = string.Empty;
        public long Views { get; set; }
        public long Likes { get; set; }
        public long Comments { get; set; }
        public long Shares { get; set; }
        public long Saves { get; set; }
        public long CompletedViews { get; set; }
        public long FollowersGained { get; set; }
        public double? EngRate { get; set; }
        public double? CompletionRate { get; set; }
    }

    public class ScatterPoint
    {
        public string PostId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public long Views { get; set; }
        public double? CompletionRate { get; set; }
    }

    public class PostDetailResponse
    {
        public PostItem Post { get; set; } = new();
        public List<SnapshotHistoryItem> Snapshots { get; set; } = new();
    }

    public class SnapshotHistoryItem
    {
        public string CapturedAt { get; set; } = string.Empty;
        public long Views { get; set; }
        public long Likes { get; set; }
        public long Comments { get; set; }
        public long Shares { get; set; }
        public long Saves { get; set; }
        public long CompletedViews { get; set; }
        public double WatchTimeSec { get; set; }
        public long FollowersGained { get; set; }
    }
}
