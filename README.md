# RC-600 Patch Manager

A Python tool for managing Roland RC-600 Loop Station patches and memory slots.

## Features

- Parse and read RC-600 memory files (.RC0 format)
- Update patch names from CSV files
- Copy effects and assignments between memory slots
- Configure track input setups
- Create setlists by organizing patches into specific memory slots
- Handle RC-600's dual-bank memory system (A/B banks with version counting)

## Files

- `rc600_patch_manager.py` - Core library with Memory and Track classes, includes CLI menu
- `rc600_tui.py` - Modern TUI application built with Textual
- `test_midi.py` - MIDI testing utilities
- `requirements.txt` - Python dependencies

## Installation

```bash
# Clone or download the repository
cd ROLAND

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (for TUI version)
pip install -r requirements.txt
```

## Usage

### TUI (Text User Interface) - Recommended

Run the modern terminal interface:

```bash
python3 rc600_tui.py
```

Features:
- Modern, interactive terminal UI with mouse and keyboard support
- **Performance Optimizations**:
  - Patches are cached after first load for instant access
  - Modified patches shown with • indicator
  - Changes staged in memory before saving to disk
  - Global "Apply All Changes" button to save all modifications at once
- **Two-panel layout**:
  - **Left panel**: Live view of all patches (slots 0-99) with their names
  - **Right panel**: Detailed view of selected patch showing:
    - **Pending Changes Counter** - Shows how many patches have unsaved changes (names, copy operations, track settings)
    - **Editable patch name** - Edit and stage name changes (not saved until Apply)
    - **Copy Settings** - Stage copy operations (effects and assigns) to multiple targets
    - Patch bank, count, and BPM information
    - **Clickable Track Table** - Click any track to edit detailed settings:
      - Playback settings (Reverse, One Shot, Playback FX, Balance, Play Level)
      - Track type & modes (Track Type, Tempo Sync, Playback Mode, Start/Stop/Overdub modes)
      - FX assignments (FX1, FX2, FX3)
      - Timing settings (Rhythm Sync, Quantize)
      - All changes staged and applied together
    - Track input configurations (Mic 1/2, Inst 1L/1R/2L/2R, Rhythm) in table format
    - Scrollable view to see all track details
- **Tools menu** accessible via keyboard shortcuts:
  - `R` - Refresh patches
  - `U` - Update patch names from CSV
  - `I` - Configure track inputs
  - `S` - Create setlist from CSV
  - `P` - Change DATA path
  - `Q` - Quit
- Visual path selection with status indicators
- Real-time status notifications
- Auto-refresh patch list after operations complete

### CLI Menu (Simple)

Run the simple command-line menu:

```bash
python3 rc600_patch_manager.py
```

The menu will:
1. Prompt you to select a DATA path (automatically detects `/Volumes/RC-600/ROLAND/DATA` or `./DATA`)
2. Present options to:
   - Update patch names from CSV
   - Configure track inputs (mic settings)
   - Create setlist from CSV
   - List memory slots
   - Exit

### Programmatic Usage

```python
from rc600_patch_manager import Memory

# Set the path to your RC-600 DATA folder
Memory.cwd = '/Volumes/RC-600/ROLAND/DATA'

# Load a memory slot
mem = Memory(38)
print(mem.name)  # Print patch name
print(mem.tracks)  # Access tracks
```

### CSV File Formats

#### Patch Names CSV (lista.csv)
Should contain `Banco` (memory slot number) and `ShortName` columns:
```csv
Banco,ShortName
30,My Patch 1
31,My Patch 2
```

#### Setlist CSV
Same format - organizes patches into sequential memory slots starting from slot 1:
```csv
Banco,ShortName
38,Song 1
42,Song 2
15,Song 3
```

## RC-600 File Format

The RC-600 uses an XML-based format with special characteristics:
- Numeric tags are converted to `NUM_X` format for XML parsing
- Hash tags (`#`) are converted to `HASH`
- Dual-bank system (A/B) with hex version counters to track latest changes
- Files are named `MEMORYXXXN.RC0` where XXX is the slot number (001-200) and N is the bank (A or B)

## Requirements

- Python 3.8+
- For TUI: `textual>=0.47.0` (installed via requirements.txt)
- For CLI: Standard library only (csv, xml.etree.ElementTree, os, sys, re, copy)

## License

MIT
