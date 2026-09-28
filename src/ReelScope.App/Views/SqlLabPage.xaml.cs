using System;
using System.Text.Json;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace ReelScope.App.Views
{
    public partial class SqlLabPage : Page
    {
        public SqlLabPage()
        {
            this.InitializeComponent();
            SqlEditorBox.Text = @"SELECT
    platform,
    COUNT(*) AS posts_count,
    SUM(views) AS total_views,
    ROUND(100.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(views), 0), 2) AS engagement_rate
FROM view_latest_posts
GROUP BY platform
ORDER BY total_views DESC;";
        }

        private async void OnRunQueryClicked(object sender, RoutedEventArgs e)
        {
            string query = SqlEditorBox.Text.Trim();
            if (string.IsNullOrEmpty(query)) return;

            try
            {
                var payload = new { query = query, limit = 100 };
                var resp = await App.Api.PostAsync<object, JsonElement>("/api/sql/query", payload);

                if (resp.TryGetProperty("rows", out var rows) && rows.ValueKind == JsonValueKind.Array)
                {
                    int count = rows.GetArrayLength();
                    TxtResultCount.Text = $"{count} rows returned";
                    ResultsListView.ItemsSource = rows.EnumerateArray();
                }
            }
            catch (Exception ex)
            {
                TxtResultCount.Text = $"Error: {ex.Message}";
            }
        }

        private void OnSampleSelected(object sender, SelectionChangedEventArgs e)
        {
            if (SqlEditorBox == null) return;

            if (sender is ComboBox cb)
            {
                SqlEditorBox.Text = cb.SelectedIndex switch
                {
                    0 => @"SELECT
    platform,
    COUNT(*) AS posts_count,
    SUM(views) AS total_views,
    ROUND(100.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(views), 0), 2) AS engagement_rate
FROM view_latest_posts
GROUP BY platform
ORDER BY total_views DESC;",
                    1 => @"SELECT
    post_id,
    platform,
    title,
    views_24h,
    velocity_24h,
    growth_ratio_7d_24h
FROM view_post_growth_milestones
WHERE views_24h IS NOT NULL
ORDER BY velocity_24h DESC
LIMIT 20;",
                    _ => @"SELECT post_id, platform, title, views, eng_rate 
FROM view_latest_posts 
WHERE views > 200000 
ORDER BY views DESC;"
                };
            }
        }
    }
}
