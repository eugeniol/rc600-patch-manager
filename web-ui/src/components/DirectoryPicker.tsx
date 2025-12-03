import { useRC600Store } from '../stores/useRC600Store';

export function DirectoryPicker() {
  const { directoryHandle, dataPath, setDirectoryHandle, setDataPath, loadPatches } = useRC600Store();

  // Check if File System Access API is supported
  const isSupported = 'showDirectoryPicker' in window;

  const handleSelectDirectory = async () => {
    if (!isSupported) {
      alert('Your browser does not support the File System Access API. Please use Chrome, Edge, or Opera.');
      return;
    }

    try {
      // Use File System Access API to pick a directory
      const handle = await window.showDirectoryPicker({
        id: 'rc600-data',
        mode: 'readwrite',
        startIn: 'downloads',
      });

      setDirectoryHandle(handle);
      setDataPath(handle.name);

      // Load patches from the selected directory
      await loadPatches();
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        console.error('Failed to select directory:', error);
      }
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">RC-600 DATA Directory</h2>

      {!isSupported ? (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h3 className="font-semibold text-red-900 dark:text-red-200 mb-1">Browser Not Supported</h3>
              <p className="text-sm text-red-800 dark:text-red-300 mb-3">
                This application requires the File System Access API, which is not available in your current browser.
              </p>
              <div className="text-sm text-red-800 dark:text-red-300">
                <p className="font-medium mb-1">Supported browsers:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Chrome 86+</li>
                  <li>Edge 86+</li>
                  <li>Opera 72+</li>
                </ul>
                <p className="mt-3 text-xs">
                  Note: Firefox and Safari do not currently support this API.
                  <br />
                  Consider using the Python TUI version (<code className="bg-red-100 dark:bg-red-800 px-1 rounded">rc600_tui.py</code>) instead.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : !directoryHandle ? (
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Select the DATA directory from your RC-600 to get started
          </p>
          <button
            onClick={handleSelectDirectory}
            className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            Select Directory
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Connected to:</p>
              <p className="font-medium text-gray-800 dark:text-gray-200">{dataPath}</p>
            </div>
          </div>
          <button
            onClick={handleSelectDirectory}
            className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Change Directory
          </button>
        </div>
      )}
    </div>
  );
}
