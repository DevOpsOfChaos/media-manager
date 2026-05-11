use serde_json::Value;

use super::python_bridge::PythonBridge;

fn bridge() -> Result<&'static PythonBridge, String> {
    PythonBridge::get().as_ref().map_err(|e| e.clone())
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
    let _ = journal_path;
    Err("media_commands: undo_preview not yet implemented".into())
}

#[tauri::command]
pub async fn undo_apply(journal_path: String) -> Result<Value, String> {
    let _ = journal_path;
    Err("media_commands: undo_apply not yet implemented".into())
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
