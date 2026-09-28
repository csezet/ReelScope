using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using ReelScope.App.Models;
using ReelScope.App.ViewModels;

namespace ReelScope.App.Views
{
    public partial class PostsPage : Page
    {
        public PostsViewModel ViewModel { get; }

        public PostsPage()
        {
            this.InitializeComponent();
            ViewModel = new PostsViewModel(App.Api);
            this.DataContext = ViewModel;

            this.Loaded += PostsPage_Loaded;
        }

        private async void PostsPage_Loaded(object sender, RoutedEventArgs e)
        {
            await ViewModel.LoadPostsAsync();
            PostsListView.ItemsSource = ViewModel.Posts;
        }

        private void OnPostSelected(object sender, SelectionChangedEventArgs e)
        {
            if (PostsListView.SelectedItem is PostItem selected)
            {
                ViewModel.SelectedPost = selected;
            }
        }
    }
}
