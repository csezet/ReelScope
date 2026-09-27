using System.Collections.ObjectModel;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using ReelScope.App.Services;

namespace ReelScope.App.ViewModels
{
    public class ImportViewModel : ViewModelBase
    {
        private readonly ApiClient _api;
        private bool _isUploading;
        private int _currentStep = 1;
        private string? _selectedFilePath;
        private string? _fileHash;
        private string _statusMessage = string.Empty;

        public bool IsUploading { get => _isUploading; set => SetField(ref _isUploading, value); }
        public int CurrentStep { get => _currentStep; set => SetField(ref _currentStep, value); }
        public string? SelectedFilePath { get => _selectedFilePath; set => SetField(ref _selectedFilePath, value); }
        public string StatusMessage { get => _statusMessage; set => SetField(ref _statusMessage, value); }

        public ObservableCollection<string> DetectedColumns { get; } = new();

        public ImportViewModel(ApiClient api)
        {
            _api = api;
        }

        public void SetStep(int step)
        {
            CurrentStep = step;
        }
    }
}
