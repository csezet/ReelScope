using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using ReelScope.App.ViewModels;

namespace ReelScope.App.Views
{
    public partial class ExperimentsPage : Page
    {
        public ExperimentsViewModel ViewModel { get; }

        public ExperimentsPage()
        {
            this.InitializeComponent();
            ViewModel = new ExperimentsViewModel(App.Api);
            this.DataContext = ViewModel;

            this.Loaded += ExperimentsPage_Loaded;
        }

        private async void ExperimentsPage_Loaded(object sender, RoutedEventArgs e)
        {
            await ViewModel.RunAnalysisAsync();

            TxtControlTitle.Text = ViewModel.ControlTitle;
            TxtControlN.Text = $"{ViewModel.ControlSampleSize:N0}";
            TxtControlRate.Text = $"{ViewModel.ControlRate:F1}%";

            TxtTreatmentTitle.Text = ViewModel.TreatmentTitle;
            TxtTreatmentN.Text = $"{ViewModel.TreatmentSampleSize:N0}";
            TxtTreatmentRate.Text = $"{ViewModel.TreatmentRate:F1}%";

            TxtAbsLift.Text = ViewModel.AbsoluteLift;
            TxtRelLift.Text = ViewModel.RelativeLift;
            TxtCI.Text = ViewModel.ConfidenceInterval;
            TxtPVal.Text = ViewModel.PValue;

            try
            {
                await BootstrapWebView.EnsureCoreWebView2Async();
                BootstrapWebView.NavigateToString(GetBootstrapChartHtml());
            }
            catch
            {
                // Fallback
            }
        }

        private string GetBootstrapChartHtml()
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
    <div id='bootstrapChart' style='width:100%;height:190px;'></div>
    <script>
        var bins = [-0.01, -0.005, 0.0, 0.005, 0.01, 0.015, 0.016, 0.02, 0.025, 0.03, 0.035, 0.04];
        var counts = [40, 150, 420, 1100, 2200, 3100, 2800, 1800, 850, 280, 70, 15];
        var data = [{
            x: bins,
            y: counts,
            type: 'bar',
            marker: { color: '#8957E5' }
        }];
        var layout = {
            margin: { t: 10, r: 10, l: 40, b: 30 },
            paper_bgcolor: '#0D1117',
            plot_bgcolor: '#0D1117',
            xaxis: { gridcolor: '#21262D', color: '#8B949E' },
            yaxis: { gridcolor: '#21262D', color: '#8B949E' }
        };
        Plotly.newPlot('bootstrapChart', data, layout, {responsive: true, displayModeBar: false});
    </script>
</body>
</html>";
        }
    }
}
