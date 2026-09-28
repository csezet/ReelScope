using System;
using Microsoft.UI.Xaml;
using ReelScope.App.Services;

namespace ReelScope.App
{
    public partial class App : Application
    {
        public static EngineProcessService EngineService { get; private set; } = null!;
        public static ApiClient Api { get; private set; } = null!;
        public static Window MainWindow { get; private set; } = null!;

        public App()
        {
            this.InitializeComponent();
            EngineService = new EngineProcessService();
            Api = new ApiClient(EngineService);
        }

        protected override async void OnLaunched(LaunchActivatedEventArgs args)
        {
            MainWindow = new MainWindow();
            MainWindow.Activate();

            // Start Python analytics engine asynchronously
            try
            {
                await EngineService.StartAsync();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error starting analytics engine: {ex.Message}");
            }
        }
    }
}
