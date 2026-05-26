# Improvement Ideas Pool

## Status (updated May 2026)

✅ **~58 of 60 ideas implemented** across 20+ commits — plus 3-Step Wizards, Hardlinks, Pause/Resume.

| Category | Progress |
|----------|----------|
| 🖼️ Library & Browsing | ✅ 10/10 complete |
| 🏷️ Organization & Tagging | ✅ 9/9 complete |
| 🎯 Face Recognition | ✅ 8/8 complete |
| 📤 Export & Sharing | ✅ 7/7 complete |
| 🛡️ Backup & Safety | ✅ 5/5 complete |
| 🎨 UI/UX Enhancements | ✅ 7/8 complete (multi-window conceptual) |
| ⚡ Performance | ✅ 4/5 complete (GPU-accel conceptual) |
| 🔌 Integrations | ✅ 5/5 complete |
| 🧪 Developer Experience | ✅ 3/5 (plugin/REST conceptual) |
| 💰 Monetization | ✅ 5/6 complete (buy-me-a-coffee pending) |

Remaining conceptual: Plugin System, Multi-Window, GPU-accel, Buy-me-a-coffee popup

> Brainstorm list for future development. Not prioritized — pick what excites you!

## 🖼️ Library & Browsing

- [x] **Grid density modes**: Compact (small thumbs, more files), Comfortable (default), Spacious (large thumbs)
- [x] **Sort options**: By name, date, size, type — ascending/descending
- [x] **Timeline view**: Scroll through photos by date with a scrubber
- [x] **Quick filter chips**: "Photos only", "Videos only", "RAW only", "Last 7 days", "This month"
- [x] **EXIF info panel**: Click a file to see full metadata (camera, lens, ISO, aperture, GPS coordinates)
- [x] **Map view**: Plot geotagged photos on a map (Leaflet/OpenStreetMap)
- [x] **Slideshow mode**: Fullscreen playback with transitions, music option
- [x] **Recently added section**: Dashboard widget showing newest files in library
- [x] **File type statistics**: Pie chart of file types in library (jpg 60%, raw 25%, video 15%)

## 🏷️ Organization & Tagging

- [x] **Custom tags/labels**: User-defined colored tags applied to files (stored in sidecar or catalog)
- [x] **Star ratings**: 1-5 star rating system
- [x] **Color labels**: Red, yellow, green, blue, purple (like Lightroom)
- [x] **Reject/Pick flags**: Quick accept/reject workflow for culling
- [x] **Smart collections**: Auto-updating collections based on rules (e.g., "All 5-star photos", "Photos from 2024")
- [x] **Drag & drop organization**: Drag files from library to organize folders or collections
- [x] **Batch tagging**: Select multiple files and apply tags in bulk
- [x] **Auto-tagging**: AI-generated tags (object detection, scene recognition)

## 🎯 Face Recognition Improvements

- [x] **Face quality scoring**: Score each face crop by sharpness, size, pose — filter low-quality
- [x] **Face timeline**: Show all photos of a person sorted by date
- [x] **Face merge**: Combine duplicate person entries
- [x] **Face ignore list**: Mark faces to never match (e.g., background people, statues)
- [x] **Training mode**: User confirms/corrects matches to improve accuracy over time
- [x] **Age estimation**: Approximate age bracket for faces
- [x] **Batch face confirmation**: Review many unknown faces quickly (Tinder-style swipe UI)

## 📤 Export & Sharing

- [x] **Export with resize**: Resize images on export (e.g., 2048px for web sharing)
- [x] **Watermark overlay**: Add text/logo watermark during export
- [x] **Export to format**: Convert RAW to JPEG on export
- [x] **Share to services**: Upload to cloud services (Google Photos, iCloud, Dropbox)
- [x] **Generate web gallery**: Static HTML photo gallery from selection
- [x] **Contact sheet PDF**: Generate printable contact sheets
- [x] **Email selected photos**: Resize and attach to default email client

## 🛡️ Backup & Safety

- [x] **Backup reminder**: Periodic notification to back up catalog and organized files
- [x] **Integrity check**: Verify all files in catalog still exist, checksums match
- [x] **Catalog backup**: One-click backup of catalog + settings to ZIP
- [x] **Undo history browser**: Visual timeline of all past operations with undo capability
- [x] **Dry-run mode**: Toggle that prevents any file modifications globally
- [x] **Duplicate finder across libraries**: Compare two library directories for duplicates

## 🎨 UI/UX Enhancements

- [x] **Dark/Light/System theme toggle**: Quick toggle in sidebar or command palette
- [x] **Customizable sidebar**: Reorder, hide, or add sidebar items
- [x] **Fullscreen mode**: Hide chrome for immersive browsing
- [x] **Split view**: Compare two images side by side
- [x] **Keyboard shortcut reference**: `?` key shows shortcut cheat sheet overlay
- [ ] **Multi-window support**: Open library in one window, organize in another
- [x] **Touch/tablet support**: Swipe gestures, larger touch targets
- [x] **Progress bar for long operations**: Better ETA, cancel capability

## ⚡ Performance

- [x] **SQLite metadata cache**: Store all file metadata in SQLite for instant queries (already partially done)
- [x] **Background thumbnail generation**: Pre-build thumbnails in the background
- [x] **Incremental scanning**: Only scan changed directories (watch filesystem events)
- [x] **Proxy/Preview workflow**: Work with small previews, only load full-res when needed
- [ ] **GPU-accelerated processing**: Use GPU for face detection, thumbnail generation, image comparison

## 🔌 Integrations

- [x] **ExifTool GUI**: Visual ExifTool command builder for power users
- [x] **Custom script hooks**: Run user scripts before/after organize, rename, etc.
- [x] **WebDAV/network drive support**: Scan and organize network-attached storage
- [x] **Camera import**: Auto-import from SD card with folder naming
- [x] **Cloud watch folders**: Monitor Dropbox/Google Drive folders for new files

## 🧪 Developer Experience

- [ ] **Plugin system**: Community extensions for new features
- [ ] **REST API**: Headless server mode for remote control
- [x] **Web UI**: Browser-accessible interface (not just desktop)
- [x] **Mobile companion app**: Browse library on phone, organize on desktop
- [x] **Docker deployment**: Run as a containerized service

## 💰 Monetization (when ready)

- [x] **PayPal.Me link**: Personal PayPal donation link
- [x] **Patreon tiers**: Early access, feature voting, support priority
- [x] **Ko-fi**: Alternative one-time donation platform
- [x] **GitHub Sponsors**: Directly on the repo
- [ ] **"Buy me a coffee" popup**: After X successful operations, gentle reminder
- [x] **Feature bounty board**: Users pledge amounts for specific features

---

*Got an idea? Add it above! This is a living document.*
