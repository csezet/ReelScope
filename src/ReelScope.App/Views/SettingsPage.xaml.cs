using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using ReelScope.App.ViewModels;

namespace ReelScope.App.Views
{
    public partial class SettingsPage : Page
    {
        public SettingsViewModel ViewModel { get; }

        public SettingsPage()
        {
            this.InitializeComponent();
            ViewModel = new SettingsViewModel(App.Api);
            this.DataContext = ViewModel;

            this.Loaded += SettingsPage_Loaded;
        }

        private async void SettingsPage_Loaded(object sender, RoutedEventArgs e)
        {
            TxtDbPath.Text = ViewModel.DatabasePath;
            await ViewModel.RefreshStatusAsync();

            TxtEngineStatus.Text = $"{ViewModel.EngineStatus} • Python {ViewModel.PythonVersion}";
            TxtDuckDbStatus.Text = $"Connected • DuckDB {ViewModel.DuckDbVersion}";
        }

        private async void OnResetDbClicked(object sender, RoutedEventArgs e)
        {
            await ViewModel.ResetDatabaseAsync();
            await ViewModel.RefreshStatusAsync();
        }
    }
}
