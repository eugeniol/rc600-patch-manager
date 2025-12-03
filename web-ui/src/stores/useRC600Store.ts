import { create } from "zustand";
import { Patch, CopyOperation } from "../types/rc600";
import { loadPatch } from "../utils/rc600Parser";

interface RC600State {
  // Directory and file system
  directoryHandle: FileSystemDirectoryHandle | null;
  dataPath: string | null;

  // Patches data
  patches: Map<number, Patch>;
  loadingPatches: boolean;

  // UI state
  selectedPatchSlot: number | null;
  pendingChanges: Set<number>;

  // Operations
  copyOperation: CopyOperation | null;

  // Actions
  setDirectoryHandle: (handle: FileSystemDirectoryHandle | null) => void;
  setDataPath: (path: string | null) => void;
  loadPatches: () => Promise<void>;
  getPatch: (slot: number) => Patch | undefined;
  updatePatchName: (slot: number, name: string) => void;
  selectPatch: (slot: number) => void;
  setCopyOperation: (operation: CopyOperation | null) => void;
  applyChanges: () => Promise<void>;
  clearPendingChanges: () => void;
  hasPendingChanges: () => boolean;
}

export const useRC600Store = create<RC600State>((set, get) => ({
  // Initial state
  directoryHandle: null,
  dataPath: null,
  patches: new Map<number, Patch>(),
  loadingPatches: false,
  selectedPatchSlot: null,
  pendingChanges: new Set<number>(),
  copyOperation: null,

  // Actions
  setDirectoryHandle: (handle) => set({ directoryHandle: handle }),

  setDataPath: (path) => set({ dataPath: path }),

  loadPatches: async () => {
    const { directoryHandle } = get();
    if (!directoryHandle) {
      console.warn("[RC600 Store] No directory handle available");
      return;
    }

    // //console.log ('[RC600 Store] Starting to load patches...');
    set({ loadingPatches: true });

    try {
      const patches = new Map<number, Patch>();

      // Load patches for slots 0-99 (100 patches total)
      // RC-600 supports slots 1-200, but we'll start with 0-99
      const totalSlots = 100;
      let successCount = 0;
      let failCount = 0;

      //console.log (`[RC600 Store] Loading ${totalSlots} patches...`);

      for (let slot = 0; slot < totalSlots; slot++) {
        try {
          const patch = await loadPatch(directoryHandle, slot);
          if (patch) {
            patches.set(slot, patch);
            successCount++;

            // Log every 10th patch
            if ((slot + 1) % 10 === 0) {
              //console.log (`[RC600 Store] Progress: ${slot + 1}/${totalSlots} patches loaded`);
            }
          } else {
            failCount++;
          }
        } catch (error) {
          console.error(`[RC600 Store] Error loading patch ${slot}:`, error);
          failCount++;
        }
      }

      //console.log (`[RC600 Store] Loading complete! Success: ${successCount}, Failed: ${failCount}`);
      //console.log (`[RC600 Store] Total patches in map:`, patches.size);

      set({ patches, loadingPatches: false });

      // Auto-select first patch if available
      if (patches.size > 0) {
        const firstSlot = Array.from(patches.keys())[0];
        set({ selectedPatchSlot: firstSlot });
        //console.log (`[RC600 Store] Auto-selected patch ${firstSlot}`);
      }
    } catch (error) {
      console.error("[RC600 Store] Fatal error loading patches:", error);
      set({ loadingPatches: false });
    }
  },

  getPatch: (slot) => {
    console.log (`[RC600 Store] Getting patch for slot ${slot}`);
    const p=get().patches.get(slot);
    console.log (`[RC600 Store] Patch for slot ${slot}:`, p);
    return p;
  },

  updatePatchName: (slot, name) => {
    const { patches, pendingChanges } = get();
    const patch = patches.get(slot);

    if (patch) {
      const updatedPatch = { ...patch, name, modified: true };
      const newPatches = new Map(patches);
      newPatches.set(slot, updatedPatch);

      const newPendingChanges = new Set(pendingChanges);
      newPendingChanges.add(slot);

      set({ patches: newPatches, pendingChanges: newPendingChanges });
    }
  },

  selectPatch: (slot) => {
    
    return set({ selectedPatchSlot: slot });
  },

  setCopyOperation: (operation) => set({ copyOperation: operation }),

  applyChanges: async () => {
    const { directoryHandle } = get();
    if (!directoryHandle) return;

    try {
      // TODO: Implement saving logic
      // This would write modified patches back to .RC0 files
      // Will need to access patches and pendingChanges to save them

      // Clear pending changes after successful save
      set({ pendingChanges: new Set() });
    } catch (error) {
      console.error("Failed to apply changes:", error);
    }
  },

  clearPendingChanges: () => set({ pendingChanges: new Set() }),

  hasPendingChanges: () => get().pendingChanges.size > 0,
}));
