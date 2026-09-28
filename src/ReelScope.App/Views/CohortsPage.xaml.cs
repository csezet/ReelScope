using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using ReelScope.App.ViewModels;

namespace ReelScope.App.Views
{
    public partial class CohortsPage : Page
    {
        public CohortsViewModel ViewModel { get; }

        public CohortsPage()
        {
            this.InitializeComponent();
            ViewModel = new CohortsViewModel(App.Api);
            this.DataContext = ViewModel;

            this.Loaded += CohortsPage_Loaded;
        }

        private async void CohortsPage_Loaded(object sender, RoutedEventArgs e)
        {
            await ViewModel.LoadCohortsAsync();
            CohortInsightsList.ItemsSource = ViewModel.Insights;

            try
            {
                await HeatmapWebView.EnsureCoreWebView2Async();
                HeatmapWebView.NavigateToString(GetHeatmapHtml());
            }
            catch
            {
                // Fallback
            }
        }

        private string GetHeatmapHtml()
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
    <div id='heatmap' style='width:100%;height:250px;'></div>
    <script>
        var zValues = [
            [100, 42, 28, 18, 12, 8, 6],
            [100, 46, 32, 21, 14, 9, 7],
            [100, 58, 45, 36, 24, 18, 12],
            [100, 49, 34, 26, 17, 12, 9],
            [100, 44, 31, 22, 15, 10, 7]
        ];
        var yMonths = ['Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024'];
        var xDays = ['Day 0', 'Day 1', 'Day 3', 'Day 7', 'Day 14', 'Day 21', 'Day 30'];
        
        var data = [{
            z: zValues,
            x: xDays,
            y: yMonths,
            type: 'heatmap',
            colorscale: [
                [0, '#0D1117'],
                [0.2, '#0C2D48'],
                [0.5, '#145DA0'],
                [0.8, '#2E8BC0'],
                [1.0, '#00D2FF']
            ],
            showscale: false
        }];
        var layout = {
            margin: { t: 10, r: 10, l: 70, b: 30 },
            paper_bgcolor: '#0D1117',
            plot_bgcolor: '#0D1117',
            xaxis: { color: '#8B949E' },
            yaxis: { color: '#8B949E' }
        };
        Plotly.newPlot('heatmap', data, layout, {responsive: true, displayModeBar: false});
    </script>
</body>
</html>";
        }
    }
}
