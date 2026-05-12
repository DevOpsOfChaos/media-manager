mod commands;

use commands::media_commands;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
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
            // People
            media_commands::people_scan,
            // History
            media_commands::history_list,
            media_commands::history_get,
            // Undo
            media_commands::undo_preview,
            media_commands::undo_apply,
            // Diagnostics
            media_commands::runtime_diagnostics,
            // Doctor
            media_commands::doctor_check,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
