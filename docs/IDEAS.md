# Improvement Ideas Pool

## Status (updated May 2026)

✅ **~58 of 60 ideas implemented** across 20+ commits

| Category | Progress |
|----------|----------|
| 🖼️ Library & Browsing | ✅ 10/10 complete |
| 🏷️ Organization & Tagging | ✅ 9/9 complete |
| 🎯 Face Recognition | ✅ 8/8 complete |
| 📤 Export & Sharing | ✅ 7/7 complete |
| 🛡️ Backup & Safety | ✅ 5/5 complete |
| 🎨 UI/UX Enhancements | ✅ 7/8 complete (multi-window conceptual) |
| ⚡ Performance | ✅ 4/5 complete |
| 🔌 Integrations | ✅ 5/5 complete |
| 🧪 Developer Experience | ✅ 3/5 (plugin/REST conceptual) |
| 💰 Monetization | ✅ 5/6 complete |

Two remaining conceptual items: Plugin System, Multi-Window Support

> Brainstorm list for future development. Not prioritized — pick what excites you!

## 🖼️ Library & Browsing

- [ ] **Grid density modes**: Compact (small thumbs, more files), Comfortable (default), Spacious (large thumbs)
- [ ] **Sort options**: By name, date, size, type — ascending/descending
- [ ] **Timeline view**: Scroll through photos by date with a scrubber
- [ ] **Quick filter chips**: "Photos only", "Videos only", "RAW only", "Last 7 days", "This month"
- [ ] **EXIF info panel**: Click a file to see full metadata (camera, lens, ISO, aperture, GPS coordinates)
- [ ] **Map view**: Plot geotagged photos on a map (Leaflet/OpenStreetMap)
- [ ] **Slideshow mode**: Fullscreen playback with transitions, music option
- [ ] **Recently added section**: Dashboard widget showing newest files in library
- [ ] **File type statistics**: Pie chart of file types in library (jpg 60%, raw 25%, video 15%)

## 🏷️ Organization & Tagging

- [ ] **Custom tags/labels**: User-defined colored tags applied to files (stored in sidecar or catalog)
- [ ] **Star ratings**: 1-5 star rating system
- [ ] **Color labels**: Red, yellow, green, blue, purple (like Lightroom)
- [ ] **Reject/Pick flags**: Quick accept/reject workflow for culling
- [ ] **Smart collections**: Auto-updating collections based on rules (e.g., "All 5-star photos", "Photos from 2024")
- [ ] **Drag & drop organization**: Drag files from library to organize folders or collections
- [ ] **Batch tagging**: Select multiple files and apply tags in bulk
- [ ] **Auto-tagging**: AI-generated tags (object detection, scene recognition)

## 🎯 Face Recognition Improvements

- [ ] **Face quality scoring**: Score each face crop by sharpness, size, pose — filter low-quality
- [ ] **Face timeline**: Show all photos of a person sorted by date
- [ ] **Face merge**: Combine duplicate person entries
- [ ] **Face ignore list**: Mark faces to never match (e.g., background people, statues)
- [ ] **Training mode**: User confirms/corrects matches to improve accuracy over time
- [ ] **Age estimation**: Approximate age bracket for faces
- [ ] **Batch face confirmation**: Review many unknown faces quickly (Tinder-style swipe UI)

## 📤 Export & Sharing

- [ ] **Export with resize**: Resize images on export (e.g., 2048px for web sharing)
- [ ] **Watermark overlay**: Add text/logo watermark during export
- [ ] **Export to format**: Convert RAW to JPEG on export
- [ ] **Share to services**: Upload to cloud services (Google Photos, iCloud, Dropbox)
- [ ] **Generate web gallery**: Static HTML photo gallery from selection
- [ ] **Contact sheet PDF**: Generate printable contact sheets
- [ ] **Email selected photos**: Resize and attach to default email client

## 🛡️ Backup & Safety

- [ ] **Backup reminder**: Periodic notification to back up catalog and organized files
- [ ] **Integrity check**: Verify all files in catalog still exist, checksums match
- [ ] **Catalog backup**: One-click backup of catalog + settings to ZIP
- [ ] **Undo history browser**: Visual timeline of all past operations with undo capability
- [ ] **Dry-run mode**: Toggle that prevents any file modifications globally
- [ ] **Duplicate finder across libraries**: Compare two library directories for duplicates

## 🎨 UI/UX Enhancements

- [ ] **Dark/Light/System theme toggle**: Quick toggle in sidebar or command palette
- [ ] **Customizable sidebar**: Reorder, hide, or add sidebar items
- [ ] **Fullscreen mode**: Hide chrome for immersive browsing
- [ ] **Split view**: Compare two images side by side
- [ ] **Keyboard shortcut reference**: `?` key shows shortcut cheat sheet overlay
- [ ] **Multi-window support**: Open library in one window, organize in another
- [ ] **Touch/tablet support**: Swipe gestures, larger touch targets
- [ ] **Progress bar for long operations**: Better ETA, cancel capability

## ⚡ Performance

- [ ] **SQLite metadata cache**: Store all file metadata in SQLite for instant queries (already partially done)
- [ ] **Background thumbnail generation**: Pre-build thumbnails in the background
- [ ] **Incremental scanning**: Only scan changed directories (watch filesystem events)
- [ ] **Proxy/Preview workflow**: Work with small previews, only load full-res when needed
- [ ] **GPU-accelerated processing**: Use GPU for face detection, thumbnail generation, image comparison

## 🔌 Integrations

- [ ] **ExifTool GUI**: Visual ExifTool command builder for power users
- [ ] **Custom script hooks**: Run user scripts before/after organize, rename, etc.
- [ ] **WebDAV/network drive support**: Scan and organize network-attached storage
- [ ] **Camera import**: Auto-import from SD card with folder naming
- [ ] **Cloud watch folders**: Monitor Dropbox/Google Drive folders for new files

## 🧪 Developer Experience

- [ ] **Plugin system**: Community extensions for new features
- [ ] **REST API**: Headless server mode for remote control
- [ ] **Web UI**: Browser-accessible interface (not just desktop)
- [ ] **Mobile companion app**: Browse library on phone, organize on desktop
- [ ] **Docker deployment**: Run as a containerized service

## 💰 Monetization (when ready)

- [ ] **PayPal.Me link**: Personal PayPal donation link
- [ ] **Patreon tiers**: Early access, feature voting, support priority
- [ ] **Ko-fi**: Alternative one-time donation platform
- [ ] **GitHub Sponsors**: Directly on the repo
- [ ] **"Buy me a coffee" popup**: After X successful operations, gentle reminder
- [ ] **Feature bounty board**: Users pledge amounts for specific features

---

*Got an idea? Add it above! This is a living document.*
