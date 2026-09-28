using System;
using Microsoft.UI.Composition.SystemBackdrops;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using ReelScope.App.Views;

namespace ReelScope.App
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();

            // Enable Windows 11 Mica backdrop effect
            TrySetMicaBackdrop();

            // Default landing page: Overview
            NavView.SelectedItem = NavView.MenuItems[0];
            ContentFrame.Navigate(typeof(OverviewPage));
        }

        private void TrySetMicaBackdrop()
        {
            if (MicaController.IsSupported())
            {
                this.SystemBackdrop = new MicaBackdrop();
            }
        }

        private void NavView_ItemInvoked(NavigationView sender, NavigationViewItemInvokedEventArgs args)
        {
            if (args.IsSettingsInvoked)
            {
                ContentFrame.Navigate(typeof(SettingsPage));
                return;
            }

            if (args.InvokedItemContainer is NavigationViewItem item && item.Tag is string tag)
            {
                Type? targetPage = tag switch
                {
                    "Overview" => typeof(OverviewPage),
                    "Import" => typeof(ImportPage),
                    "Posts" => typeof(PostsPage),
                    "Cohorts" => typeof(CohortsPage),
                    "Experiments" => typeof(ExperimentsPage),
                    "Segments" => typeof(SegmentsPage),
                    "SqlLab" => typeof(SqlLabPage),
                    _ => typeof(OverviewPage)
                };

                if (targetPage != null && ContentFrame.CurrentSourcePageType != targetPage)
                {
                    ContentFrame.Navigate(targetPage);
                }
            }
        }
    }
}
