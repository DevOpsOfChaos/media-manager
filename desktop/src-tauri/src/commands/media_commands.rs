use serde_json::Value;
use tauri::Emitter;

use super::python_bridge::PythonBridge;

fn bridge() -> Result<&'static PythonBridge, String> {
    PythonBridge::get().as_ref().map_err(|e| e.clone())
}

fn emit_progress(app: &tauri::AppHandle, event: &str, label: &str, detail: Option<&str>) {
    let payload = serde_json::json!({
        "label": label,
        "detail": detail,
    });
    let _ = app.emit(event, payload);
}

// ── Settings ──

#[tauri::command]
pub async fn settings_read() -> Result<Value, String> {
    bridge()?.run_module("bridge_settings", "read", &[], None)
}

#[tauri::command]
pub async fn settings_write(settings: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&settings)
        .map_err(|e| format!("Failed to serialize settings: {e}"))?;
    bridge()?.run_module("bridge_settings", "write", &[], Some(&json))
}

#[tauri::command]
pub async fn settings_reset() -> Result<Value, String> {
    bridge()?.run_module("bridge_settings", "reset", &[], None)
}

// ── Organize ──

#[tauri::command]
pub async fn organize_preview(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Organize Preview", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize organize options: {e}"))?;
    let result = bridge()?.run_module(
        "bridge_organize_preview",
        "",
        &[],
        Some(&json),
    );
    emit_progress(&app, "operation:completed", "Organize Preview",
        Some(if result.is_ok() { "success" } else { "failed" }));
    result
}

#[tauri::command]
pub async fn organize_apply(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Organize Apply", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize organize options: {e}"))?;
    let result = bridge()?.run_module(
        "bridge_organize_apply",
        "",
        &[],
        Some(&json),
    );
    emit_progress(&app, "operation:completed", "Organize Apply",
        Some(if result.is_ok() { "success" } else { "failed" }));
    result
}

// ── Duplicates ──

#[tauri::command]
pub async fn duplicates_scan(app: tauri::AppHandle, config: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Duplicate Scan", None);
    let json = serde_json::to_string(&config)
        .map_err(|e| format!("Failed to serialize duplicates config: {e}"))?;
    let result = bridge()?.run_module(
        "bridge_duplicates_preview",
        "",
        &[],
        Some(&json),
    );
    emit_progress(&app, "operation:completed", "Duplicate Scan",
        Some(if result.is_ok() { "success" } else { "failed" }));
    result
}

#[tauri::command]
pub async fn similar_images_scan(app: tauri::AppHandle, config: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Similar Images Scan", None);
    let json = serde_json::to_string(&config)
        .map_err(|e| format!("Failed to serialize similar images config: {e}"))?;
    let result = bridge()?.run_module(
        "bridge_similar_preview",
        "",
        &[],
        Some(&json),
    );
    emit_progress(&app, "operation:completed", "Similar Images Scan",
        Some(if result.is_ok() { "success" } else { "failed" }));
    result
}

#[tauri::command]
pub async fn duplicates_apply(app: tauri::AppHandle, payload: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Duplicate Deletion", None);
    let json = serde_json::to_string(&payload)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let result = bridge()?.run_module("bridge_duplicates_apply", "", &[], Some(&json));
    emit_progress(&app, "operation:completed", "Duplicate Deletion",
        Some(if result.is_ok() { "success" } else { "failed" }));
    result
}

// ── Review ──

#[tauri::command]
pub async fn review_save_session(payload: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&payload)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_review", "save-session", &[], Some(&json))
}

#[tauri::command]
pub async fn review_load_session(payload: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&payload)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_review", "load-session", &[], Some(&json))
}

// ── People ──

#[tauri::command]
pub async fn people_scan(config: Value) -> Result<Value, String> {
    let _ = config;
    Err("media_commands: people_scan not yet implemented".into())
}

// ── History / Runs ──

#[tauri::command]
pub async fn history_list() -> Result<Value, String> {
    bridge()?.run_module("bridge_history", "list", &[], None)
}

#[tauri::command]
pub async fn history_get(run_id: String) -> Result<Value, String> {
    bridge()?.run_module("bridge_history", "get", &[&run_id], None)
}

// ── Undo ──

#[tauri::command]
pub async fn undo_preview(journal_path: String) -> Result<Value, String> {
    let json = serde_json::json!({"journal_path": journal_path});
    let json_str = serde_json::to_string(&json)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_undo", "preview", &[], Some(&json_str))
}

#[tauri::command]
pub async fn undo_apply(journal_path: String) -> Result<Value, String> {
    let json = serde_json::json!({"journal_path": journal_path});
    let json_str = serde_json::to_string(&json)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_undo", "apply", &[], Some(&json_str))
}

// ── Diagnostics ──

#[tauri::command]
pub async fn runtime_diagnostics() -> Result<Value, String> {
    let b = bridge()?;

    let env_hints = serde_json::json!({
        "MEDIA_MANAGER_PYTHON": std::env::var("MEDIA_MANAGER_PYTHON").ok(),
        "VIRTUAL_ENV": std::env::var("VIRTUAL_ENV").ok(),
        "CONDA_PREFIX": std::env::var("CONDA_PREFIX").ok(),
        "MEDIA_MANAGER_PROJECT_ROOT": std::env::var("MEDIA_MANAGER_PROJECT_ROOT").ok(),
        "MEDIA_MANAGER_SETTINGS_PATH": std::env::var("MEDIA_MANAGER_SETTINGS_PATH").ok(),
    });

    let mut rust_info = serde_json::json!({
        "python_exe": b.executable(),
        "project_root": b.project_root().to_string_lossy(),
        "pythonpath_prepended": b.effective_pythonpath(),
        "settings_path_override": b.settings_path(),
        "env_hints": env_hints,
    });

    // Try to get Python-side diagnostics
    match b.run_module("bridge_diagnostics", "", &[], None) {
        Ok(py_info) => {
            if let Some(obj) = py_info.as_object() {
                for (key, value) in obj {
                    rust_info[key] = value.clone();
                }
            }
            rust_info["python_reachable"] = serde_json::Value::Bool(true);
        }
        Err(e) => {
            rust_info["python_reachable"] = serde_json::Value::Bool(false);
            rust_info["python_error"] = serde_json::Value::String(e);
        }
    }

    Ok(rust_info)
}

// ── Doctor ──

#[tauri::command]
pub async fn doctor_check() -> Result<Value, String> {
    Err("media_commands: doctor_check not yet implemented".into())
}
