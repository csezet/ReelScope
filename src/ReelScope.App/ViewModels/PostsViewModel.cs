using System;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using ReelScope.App.Models;
using ReelScope.App.Services;

namespace ReelScope.App.ViewModels
{
    public class PostsViewModel : ViewModelBase
    {
        private readonly ApiClient _api;
        private bool _isLoading;
        private string? _selectedPlatform = "All";
        private string? _selectedFormat = "All";
        private string _searchText = string.Empty;
        private string _sortBy = "published_at";
        private string _sortOrder = "desc";
        private int _totalPosts;
        private PostItem? _selectedPost;
        private PostDetailResponse? _postDetail;

        public bool IsLoading { get => _isLoading; set => SetField(ref _isLoading, value); }
        public int TotalPosts { get => _totalPosts; set => SetField(ref _totalPosts, value); }

        public string? SelectedPlatform
        {
            get => _selectedPlatform;
            set
            {
                if (SetField(ref _selectedPlatform, value))
                    _ = LoadPostsAsync();
            }
        }

        public string? SelectedFormat
        {
            get => _selectedFormat;
            set
            {
                if (SetField(ref _selectedFormat, value))
                    _ = LoadPostsAsync();
            }
        }

        public string SearchText
        {
            get => _searchText;
            set
            {
                if (SetField(ref _searchText, value))
                    _ = LoadPostsAsync();
            }
        }

        public PostItem? SelectedPost
        {
            get => _selectedPost;
            set
            {
                if (SetField(ref _selectedPost, value) && value != null)
                {
                    _ = LoadPostDetailAsync(value.PostId);
                }
            }
        }

        public PostDetailResponse? PostDetail
        {
            get => _postDetail;
            set => SetField(ref _postDetail, value);
        }

        public ObservableCollection<PostItem> Posts { get; } = new();
        public ObservableCollection<ScatterPoint> ScatterPoints { get; } = new();
        public ObservableCollection<SnapshotHistoryItem> SelectedPostSnapshots { get; } = new();

        public PostsViewModel(ApiClient api)
        {
            _api = api;
        }

        public async Task LoadPostsAsync(CancellationToken ct = default)
        {
            IsLoading = true;
            try
            {
                string plat = string.IsNullOrEmpty(SelectedPlatform) || SelectedPlatform == "All" ? "" : $"&platform={SelectedPlatform.ToLowerInvariant()}";
                string fmt = string.IsNullOrEmpty(SelectedFormat) || SelectedFormat == "All" ? "" : $"&content_type={Uri.EscapeDataString(SelectedFormat)}";
                string search = string.IsNullOrEmpty(SearchText) ? "" : $"&search={Uri.EscapeDataString(SearchText)}";

                string url = $"/api/posts?limit=100&sort_by={_sortBy}&sort_order={_sortOrder}{plat}{fmt}{search}";
                var resp = await _api.GetAsync<PostListResponse>(url, ct);

                if (resp != null)
                {
                    TotalPosts = resp.Total;
                    Posts.Clear();
                    resp.Posts.ForEach(Posts.Add);

                    ScatterPoints.Clear();
                    resp.Scatter.ForEach(ScatterPoints.Add);

                    if (SelectedPost == null && Posts.Count > 0)
                    {
                        SelectedPost = Posts[0];
                    }
                }
            }
            finally
            {
                IsLoading = false;
            }
        }

        public async Task LoadPostDetailAsync(string postId, CancellationToken ct = default)
        {
            try
            {
                var detail = await _api.GetAsync<PostDetailResponse>($"/api/posts/{postId}", ct);
                PostDetail = detail;
                SelectedPostSnapshots.Clear();
                detail?.Snapshots?.ForEach(SelectedPostSnapshots.Add);
            }
            catch
            {
                // Detail load error handling
            }
        }
    }
}
