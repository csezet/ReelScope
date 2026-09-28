using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using ReelScope.App.ViewModels;

namespace ReelScope.App.Views
{
    public partial class ImportPage : Page
    {
        public ImportViewModel ViewModel { get; }

        public ImportPage()
        {
            this.InitializeComponent();
            ViewModel = new ImportViewModel(App.Api);
            this.DataContext = ViewModel;
        }

        private void OnBrowseFileClicked(object sender, RoutedEventArgs e)
        {
            // Windows OpenFileDialog triggers file selection
        }
    }
}
