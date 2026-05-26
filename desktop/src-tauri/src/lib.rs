mod commands;

use commands::media_commands;
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
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
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
            // Diagnostics
            media_commands::runtime_diagnostics,
            // Trip
            media_commands::trip_preview,
            media_commands::trip_apply,
            // Doctor
            media_commands::doctor_check,
            // Library
            media_commands::library_browse,
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
            media_commands::read_thumbnails_batch,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
