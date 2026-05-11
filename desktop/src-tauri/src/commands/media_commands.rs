use serde_json::Value;

use super::python_bridge::PythonBridge;

fn bridge() -> Result<&'static PythonBridge, String> {
    PythonBridge::get().as_ref().map_err(|e| e.clone())
}

// ── Settings ──

#[tauri::command]
pub async fn settings_read() -> Result<Value, String> {
    bridge()?.run_module("bridge_settings", "read", None)
}

#[tauri::command]
pub async fn settings_write(settings: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&settings)
        .map_err(|e| format!("Failed to serialize settings: {e}"))?;
    bridge()?.run_module("bridge_settings", "write", Some(&json))
}

#[tauri::command]
pub async fn settings_reset() -> Result<Value, String> {
    bridge()?.run_module("bridge_settings", "reset", None)
}

// ── Organize ──

#[tauri::command]
pub async fn organize_preview(options: Value) -> Result<Value, String> {
    let _ = options;
    Err("media_commands: organize_preview not yet implemented".into())
}

#[tauri::command]
pub async fn organize_apply(plan: Value) -> Result<Value, String> {
    let _ = plan;
    Err("media_commands: organize_apply not yet implemented".into())
}

// ── Duplicates ──

#[tauri::command]
pub async fn duplicates_scan(config: Value) -> Result<Value, String> {
    let _ = config;
    Err("media_commands: duplicates_scan not yet implemented".into())
}

// ── People ──

#[tauri::command]
pub async fn people_scan(config: Value) -> Result<Value, String> {
    let _ = config;
    Err("media_commands: people_scan not yet implemented".into())
}

// ── History / Runs ──

#[tauri::command]
pub async fn runs_list() -> Result<Value, String> {
    Err("media_commands: runs_list not yet implemented".into())
}

#[tauri::command]
pub async fn runs_inspect(run_id: String) -> Result<Value, String> {
    let _ = run_id;
    Err("media_commands: runs_inspect not yet implemented".into())
}

// ── Undo ──

#[tauri::command]
pub async fn undo_preview(journal_path: String) -> Result<Value, String> {
    let _ = journal_path;
    Err("media_commands: undo_preview not yet implemented".into())
}

#[tauri::command]
pub async fn undo_apply(journal_path: String) -> Result<Value, String> {
    let _ = journal_path;
    Err("media_commands: undo_apply not yet implemented".into())
}

// ── Doctor ──

#[tauri::command]
pub async fn doctor_check() -> Result<Value, String> {
    Err("media_commands: doctor_check not yet implemented".into())
}
