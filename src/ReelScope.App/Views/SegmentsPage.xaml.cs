using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using ReelScope.App.ViewModels;

namespace ReelScope.App.Views
{
    public partial class SegmentsPage : Page
    {
        public SegmentsViewModel ViewModel { get; }

        public SegmentsPage()
        {
            this.InitializeComponent();
            ViewModel = new SegmentsViewModel(App.Api);
            this.DataContext = ViewModel;

            this.Loaded += SegmentsPage_Loaded;
        }

        private async void SegmentsPage_Loaded(object sender, RoutedEventArgs e)
        {
            await ViewModel.RunAnalysisAsync();
            TopFeaturesList.ItemsSource = ViewModel.FeatureImportance;
            SegmentStatsListView.ItemsSource = ViewModel.Clusters;

            try
            {
                await RadarWebView.EnsureCoreWebView2Async();
                RadarWebView.NavigateToString(GetRadarChartHtml());
            }
            catch
            {
                // Fallback
            }
        }

        private string GetRadarChartHtml()
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
    <div id='radar' style='width:100%;height:190px;'></div>
    <script>
        var categories = ['Views', 'Engagement', 'Saves', 'Comments', 'Shares', 'Follows'];
        var data = [
            {
                type: 'scatterpolar',
                r: [0.95, 0.85, 0.80, 0.70, 0.90, 0.88],
                theta: categories,
                fill: 'toself',
                name: 'Viral Short',
                line: { color: '#00D2FF' }
            },
            {
                type: 'scatterpolar',
                r: [0.70, 0.92, 0.88, 0.85, 0.75, 0.80],
                theta: categories,
                fill: 'toself',
                name: 'High Engagement',
                line: { color: '#F778BA' }
            }
        ];
        var layout = {
            margin: { t: 15, r: 15, l: 15, b: 15 },
            paper_bgcolor: '#0D1117',
            polar: {
                bgcolor: '#0D1117',
                radialaxis: { visible: true, range: [0, 1], gridcolor: '#21262D', color: '#8B949E' },
                angularaxis: { gridcolor: '#21262D', color: '#8B949E' }
            },
            showlegend: false
        };
        Plotly.newPlot('radar', data, layout, {responsive: true, displayModeBar: false});
    </script>
</body>
</html>";
        }
    }
}
