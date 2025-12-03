import { Header } from './components/Header';
import { DirectoryPicker } from './components/DirectoryPicker';
import { PatchList } from './components/PatchList';
import { PatchDetails } from './components/PatchDetails';
import { useRC600Store } from './stores/useRC600Store';
import { useDarkMode } from './hooks/useDarkMode';

function App() {
  const { directoryHandle } = useRC600Store();
  const { isDark, toggle } = useDarkMode();

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <Header isDark={isDark} toggleDarkMode={toggle} />

      <main className="container mx-auto px-6 py-8">
        <DirectoryPicker />

        {directoryHandle && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <PatchList />
            </div>
            <div>
              <PatchDetails />
            </div>
          </div>
        )}

        {!directoryHandle && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12">
            <div className="text-center">
              <svg
                className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-500 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Welcome to RC-600 Patch Manager
              </h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                Get started by selecting your RC-600 DATA directory above. You'll be able to view,
                edit, and manage all your patches from this interface.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
