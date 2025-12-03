# RC-600 Patch Manager - Web UI

A modern web interface for managing Roland RC-600 Loop Station patches. Built with React, Zustand, Tailwind CSS, and Zod.

## Features

- **Directory Selection**: Use HTML5 File System Access API to select your RC-600 DATA directory
- **Patch Management**: View all patches (slots 0-199) with their names, banks, and BPM
- **Live Editing**: Edit patch names with real-time preview
- **Change Tracking**: Track modified patches with visual indicators
- **Batch Operations**: Apply all changes at once or discard them
- **Responsive Design**: Modern, clean UI built with Tailwind CSS
- **Type-Safe**: Schema validation with Zod

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Build tool and dev server
- **Zustand** - State management
- **Tailwind CSS v4** - Styling
- **Zod** - Schema validation
- **File System Access API** - Directory and file access

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Modern browser with File System Access API support (Chrome, Edge, Opera)

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Usage

1. **Select Directory**: Click "Select Directory" and choose your RC-600 DATA folder
   - This is typically at `/Volumes/RC-600/ROLAND/DATA` on macOS
   - Or `E:\ROLAND\DATA` on Windows (where E: is your RC-600 drive)

2. **Browse Patches**: View all your patches in the left panel
   - Modified patches show an orange dot indicator
   - Click any patch to view details

3. **Edit Patches**: Click "Edit" on any patch name to modify it
   - Maximum 16 characters
   - Press Enter to save or Escape to cancel

4. **Apply Changes**: Click "Apply All Changes" in the header to save
   - Or click "Discard" to revert all pending changes

## Browser Compatibility

This application requires the File System Access API, which is supported in:

- Chrome 86+
- Edge 86+
- Opera 72+

**Not supported**: Firefox, Safari (as of 2024)

For unsupported browsers, consider using the TUI version (`rc600_tui.py`) or CLI version (`rc600_patch_manager.py`) instead.

## Project Structure

```
web-ui/
├── src/
│   ├── components/        # React components
│   │   ├── DirectoryPicker.tsx
│   │   ├── Header.tsx
│   │   ├── PatchList.tsx
│   │   └── PatchDetails.tsx
│   ├── stores/           # Zustand stores
│   │   └── useRC600Store.ts
│   ├── types/            # Zod schemas & TypeScript types
│   │   └── rc600.ts
│   ├── utils/            # Utility functions
│   ├── vite-env.d.ts     # TypeScript declarations (File System API)
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── index.html            # HTML template
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Future Enhancements

- [ ] Implement file reading/writing for .RC0 files
- [ ] Add copy operations between patches
- [ ] CSV import/export for patch names
- [ ] Track detail editing
- [ ] Setlist creation
- [ ] Search and filter patches
- [ ] Dark mode support

## License

MIT
