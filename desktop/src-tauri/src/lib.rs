mod commands;

use commands::media_commands;
use commands::autostart;
use tauri::Manager;
use std::fs::OpenOptions;
use std::io::Write;
use std::panic;

fn setup_crash_log() {
    let log_path = std::env::temp_dir().join("media-manager-crash.log");

    panic::set_hook(Box::new(move |info| {
        let msg = info.payload().downcast_ref::<&str>().map(|s| s.to_string())
            .or_else(|| info.payload().downcast_ref::<String>().cloned())
            .unwrap_or_else(|| "unknown panic".to_string());

        let loc = info.location().map(|l| format!("{}:{}", l.file(), l.line())).unwrap_or_default();
        let entry = format!("CRASH | {} | {}\n", msg, loc);

        if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&log_path) {
            let _ = writeln!(f, "{}", entry);
        }
        eprintln!("{}", entry);
    }));
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    setup_crash_log();
    if let Err(e) = commands::python_bridge::PythonBridge::get() {
        eprintln!("FATAL: Python bridge unavailable: {e}");
    }
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            if std::env::args().any(|arg| arg == "--background") {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.eval("window.history.replaceState(null, '', '/?background=true'); localStorage.setItem('background_launched', 'true')");
                }
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Settings
            media_commands::settings_read,
            media_commands::settings_write,
            media_commands::settings_reset,
            // Organize
            media_commands::organize_preview,
            media_commands::organize_apply,
            // Duplicates
            media_commands::duplicates_scan,
            media_commands::similar_images_scan,
            media_commands::duplicates_apply,
            // Review
            media_commands::review_save_session,
            media_commands::review_load_session,
            media_commands::review_apply_decisions,
            // People
            media_commands::people_scan,
            media_commands::people_scan_status,
            media_commands::people_scan_reset,
            media_commands::people_catalog_list,
            media_commands::people_person_rename,
            media_commands::people_person_create,
            media_commands::people_person_reassign,
            media_commands::people_person_merge,
            media_commands::people_catalog_info,
            media_commands::people_face_ignore,
            media_commands::people_face_age,
            media_commands::people_face_feedback,
            // History
            media_commands::history_list,
            media_commands::history_get,
            // Undo
            media_commands::undo_preview,
            media_commands::undo_apply,
            // Rename
            media_commands::rename_preview,
            media_commands::rename_apply,
            // Diagnostics
            media_commands::runtime_diagnostics,
            // Trip
            media_commands::trip_preview,
            media_commands::trip_apply,
            // Doctor
            media_commands::doctor_check,
            // Library
            media_commands::library_browse,
            // Stats & Search
            media_commands::library_stats,
            media_commands::size_report,
            media_commands::media_search,
            // File Operations
            media_commands::file_open,
            media_commands::file_reveal,
            media_commands::file_delete,
            media_commands::file_rename,
            media_commands::file_export,
            media_commands::file_integrity,
            media_commands::file_backup,
            media_commands::file_contact_sheet,
            media_commands::file_web_gallery,
            media_commands::file_watermark,
            media_commands::file_batch_delete,
            media_commands::file_batch_copy,
            media_commands::file_thumbnail,
            media_commands::file_thumbnails_batch,
            media_commands::file_watch_events,
            media_commands::read_thumbnails_batch,
            // Window
            media_commands::resize_window,
            media_commands::get_window_size,
            // Background
            media_commands::background_scan,
            // Enrich
            media_commands::enrich_file,
            media_commands::enrich_batch,
            // Autostart
            autostart::get_autostart_status,
            autostart::set_autostart,
            // Groups
            media_commands::groups_by_date,
            media_commands::groups_by_camera,
            media_commands::groups_by_location,
            media_commands::groups_by_people,
            media_commands::groups_timeline,
        ])
        .run(tauri::generate_context!())
        .unwrap_or_else(|e| {
            eprintln!("FATAL: Failed to run tauri application: {e}");
            std::process::exit(1);
        });
}
