import { useState } from 'react';
import { useRC600Store } from '../stores/useRC600Store';

export function PatchDetails() {
  const { selectedPatchSlot, getPatch, updatePatchName, pendingChanges } = useRC600Store();
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState('');

  if (selectedPatchSlot === null) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <p className="text-center text-gray-500 dark:text-gray-400 py-12">
          Select a patch to view details
        </p>
      </div>
    );
  }

  const patch = getPatch(selectedPatchSlot);

  if (!patch) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <p className="text-center text-red-500 dark:text-red-400 py-12">
          Patch not found
        </p>
      </div>
    );
  }

  const handleStartEdit = () => {
    setNewName(patch.name);
    setEditingName(true);
  };

  const handleSaveName = () => {
    if (newName.trim() && newName.length <= 16) {
      updatePatchName(selectedPatchSlot, newName.trim());
      setEditingName(false);
    }
  };

  const handleCancelEdit = () => {
    setEditingName(false);
    setNewName('');
  };

  const hasChanges = pendingChanges.has(selectedPatchSlot);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Patch Details</h2>
          <span className="text-sm font-mono text-gray-500 dark:text-gray-400">
            Slot {patch.slot.toString().padStart(3, '0')}
          </span>
        </div>

        {/* Patch Name */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Patch Name
            {hasChanges && (
              <span className="ml-2 text-orange-600 text-xs">● Modified</span>
            )}
          </label>
          {editingName ? (
            <div className="flex gap-2">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                maxLength={16}
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveName();
                  if (e.key === 'Escape') handleCancelEdit();
                }}
              />
              <button
                onClick={handleSaveName}
                className="bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 px-4 py-3 rounded-lg">
              <span className="font-medium text-gray-800 dark:text-gray-100">{patch.name}</span>
              <button
                onClick={handleStartEdit}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Edit
              </button>
            </div>
          )}
          {editingName && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {newName.length}/16 characters
            </p>
          )}
        </div>

        {/* Patch Info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bank</label>
            <div className="bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg">
              <span className="font-mono text-gray-800 dark:text-gray-100">{patch.bank}</span>
            </div>
          </div>
          {patch.bpm && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">BPM</label>
              <div className="bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg">
                <span className="font-mono text-gray-800 dark:text-gray-100">{patch.bpm}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tracks */}
      <div className="p-6">
        <h3 className="text-md font-semibold text-gray-800 dark:text-gray-100 mb-4">Tracks</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">Track</th>
                <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">Type</th>
                <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">FX1</th>
                <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">FX2</th>
                <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">FX3</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {patch.tracks.map((track) => (
                <tr key={track.number} className="hover:bg-gray-50">
                  <td className="py-2 px-3 font-medium text-gray-800 dark:text-gray-100">Track {track.number}</td>
                  <td className="py-2 px-3 text-gray-600 dark:text-gray-300">{track.trackType || '-'}</td>
                  <td className="py-2 px-3 text-gray-600 dark:text-gray-300">{track.fx1 || '-'}</td>
                  <td className="py-2 px-3 text-gray-600 dark:text-gray-300">{track.fx2 || '-'}</td>
                  <td className="py-2 px-3 text-gray-600 dark:text-gray-300">{track.fx3 || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
