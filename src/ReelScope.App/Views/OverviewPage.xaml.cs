using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using ReelScope.App.ViewModels;

namespace ReelScope.App.Views
{
    public partial class OverviewPage : Page
    {
        public OverviewViewModel ViewModel { get; }

        public OverviewPage()
        {
            this.InitializeComponent();
            ViewModel = new OverviewViewModel(App.Api);
            this.DataContext = ViewModel;

            this.Loaded += OverviewPage_Loaded;
        }

        private async void OverviewPage_Loaded(object sender, RoutedEventArgs e)
        {
            await ViewModel.LoadDataAsync();
            InsightsList.ItemsSource = ViewModel.Insights;
            FormatList.ItemsSource = ViewModel.FormatBreakdown;
            PlatformList.ItemsSource = ViewModel.PlatformMix;
            RecentPostsList.ItemsSource = ViewModel.RecentPosts;

            TxtViews.Text = $"{ViewModel.TotalViews:N0}";
            TxtEngRate.Text = $"{ViewModel.EngagementRate:F1}%";
            TxtCompletionRate.Text = $"{ViewModel.CompletionRate:F1}%";
            TxtSaves.Text = $"{ViewModel.Saves:N0}";
            TxtFollowers.Text = $"+{ViewModel.FollowersGained:N0}";

            // Initialize WebView2 spline chart
            try
            {
                await ChartWebView.EnsureCoreWebView2Async();
                ChartWebView.NavigateToString(GetSplineChartHtml());
            }
            catch
            {
                // WebView2 initialization fallback
            }
        }

        private async void OnLoadDemoClicked(object sender, RoutedEventArgs e)
        {
            await ViewModel.LoadDemoDatasetAsync();
            OverviewPage_Loaded(this, e);
        }

        private string GetSplineChartHtml()
        {
            return @"<!DOCTYPE html>
<html>
<head>
    <script src='https://cdn.plot.ly/plotly-2.29.0.min.js'></script>
    <style>
        body { margin: 0; background: #0D1117; color: #C9D1D9; font-family: Segoe UI, sans-serif; }
    </style>
</head>
<body>
    <div id='chart' style='width:100%;height:230px;'></div>
    <script>
        var dates = ['May 1', 'May 4', 'May 7', 'May 10', 'May 13', 'May 16', 'May 19', 'May 22', 'May 25', 'May 28', 'May 31'];
        var views = [75000, 105000, 95000, 140000, 130000, 175000, 190000, 248000, 210000, 225000, 290000];
        var trace = {
            x: dates,
            y: views,
            type: 'scatter',
            mode: 'lines',
            line: { shape: 'spline', color: '#00D2FF', width: 3 },
            fill: 'tozeroy',
            fillcolor: 'rgba(0, 210, 255, 0.12)'
        };
        var layout = {
            margin: { t: 10, r: 20, l: 40, b: 30 },
            paper_bgcolor: '#0D1117',
            plot_bgcolor: '#0D1117',
            xaxis: { gridcolor: '#21262D', color: '#8B949E' },
            yaxis: { gridcolor: '#21262D', color: '#8B949E' }
        };
        Plotly.newPlot('chart', [trace], layout, {responsive: true, displayModeBar: false});
    </script>
</body>
</html>";
        }
    }
}
