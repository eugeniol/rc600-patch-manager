import { useRC600Store } from '../stores/useRC600Store';

export function PatchList() {
  const { patches, selectedPatchSlot, selectPatch, pendingChanges, loadingPatches } = useRC600Store();

  if (loadingPatches) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-300">Loading patches...</span>
        </div>
      </div>
    );
  }

  if (patches.size === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <p className="text-center text-gray-500 dark:text-gray-400 py-12">
          No patches loaded. Select a DATA directory to get started.
        </p>
      </div>
    );
  }

  // Convert patches map to array and sort by slot number
  const patchArray = Array.from(patches.values()).sort((a, b) => a.slot - b.slot);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Patches</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {pendingChanges.size > 0 && (
            <span className="text-orange-600 font-medium">
              {pendingChanges.size} unsaved change{pendingChanges.size !== 1 ? 's' : ''}
            </span>
          )}
        </p>
      </div>

      <div className="overflow-y-auto max-h-[600px]">
        <div className="divide-y divide-gray-200">
          {patchArray.map((patch) => {
            const isSelected = selectedPatchSlot === patch.slot;
            const hasChanges = pendingChanges.has(patch.slot);

            return (
              <button
                key={patch.slot}
                onClick={() => selectPatch(patch.slot)}
                className={`w-full text-left px-4 py-3 transition-colors ${
                  isSelected
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-600 dark:border-blue-400'
                    : 'hover:bg-gray-50 dark:bg-gray-700/50 border-l-4 border-transparent'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">
                      {patch.slot.toString().padStart(3, '0')}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`font-medium ${isSelected ? 'text-blue-900 dark:text-blue-100' : 'text-gray-800 dark:text-gray-100'}`}>
                          {patch.name}
                        </span>
                        {hasChanges && (
                          <span className="w-2 h-2 bg-orange-500 rounded-full" title="Modified"></span>
                        )}
                      </div>
                      {patch.bpm && (
                        <span className="text-xs text-gray-500 dark:text-gray-400">{patch.bpm} BPM</span>
                      )}
                    </div>
                  </div>
                  <div className="text-xs text-gray-400 font-mono">
                    {patch.bank}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
