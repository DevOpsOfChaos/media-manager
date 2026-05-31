use serde_json::Value;
use tauri::Emitter;
use tauri::Manager;

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

fn emit_completion(app: &tauri::AppHandle, label: &str, result: &Result<Value, String>) {
    let detail = match result {
        Ok(val) => {
            let summary = pick_summary_keys(val);
            if summary.is_null() { "success".to_string() } else { summary.to_string() }
        }
        Err(e) => e.clone(),
    };
    emit_progress(app, "operation:completed", label, Some(&detail));
}

fn pick_summary_keys(val: &Value) -> Value {
    let obj = match val.as_object() {
        Some(o) => o,
        None => return Value::Null,
    };
    let mut summary = serde_json::Map::new();
    for key in &["executed_count", "planned_count", "renamed_count", "removed",
                  "total_faces", "matched_faces", "file_count", "exact_duplicate_files",
                  "similar_pairs", "copied_count", "moved_count", "linked_count", "undone_count"] {
        if let Some(v) = obj.get(*key) {
            summary.insert((*key).to_string(), v.clone());
        }
    }
    if summary.is_empty() { Value::Null } else { Value::Object(summary) }
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
    let (stdout_text, _stderr_text) = bridge()?.run_module_streaming(
        &app,
        "bridge_organize_preview",
        "",
        &[],
        Some(&json),
    )?;

    let mut final_line = String::new();

    for line in stdout_text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        if let Ok(entry) = serde_json::from_str::<Value>(line) {
            if entry.get("batch").is_some() {
                let _ = app.emit("organize-batch", &entry);
            } else {
                final_line = line.to_string();
            }
        }
    }

    if final_line.is_empty() {
        return Err("No final result in bridge output".into());
    }

    let result: Value = serde_json::from_str(&final_line)
        .map_err(|e| format!("Failed to parse final result: {e}\nRaw: {}", final_line))?;

    emit_completion(&app, "Organize Preview", &Ok(result.clone()));
    Ok(result)
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
    emit_completion(&app, "Organize Apply", &result);
    result
}

// ── Duplicates ──

#[tauri::command]
pub async fn duplicates_scan(app: tauri::AppHandle, config: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Duplicate Scan", None);
    let json = serde_json::to_string(&config)
        .map_err(|e| format!("Failed to serialize duplicates config: {e}"))?;
    let (stdout_text, _stderr_text) = bridge()?.run_module_streaming(
        &app,
        "bridge_duplicates_preview",
        "",
        &[],
        Some(&json),
    )?;

    let mut final_line = String::new();

    for line in stdout_text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        if let Ok(val) = serde_json::from_str::<Value>(line) {
            if val.get("files").is_some() && val.get("file_size").is_some() {
                let _ = app.emit("early-duplicate", val);
            } else {
                final_line = line.to_string();
            }
        }
    }

    if final_line.is_empty() {
        return Err("No final result in bridge output".into());
    }

    let result: Value = serde_json::from_str(&final_line)
        .map_err(|e| format!("Failed to parse final result: {e}\nRaw: {}", final_line))?;

    emit_completion(&app, "Duplicate Scan", &Ok(result.clone()));
    Ok(result)
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
    emit_completion(&app, "Similar Images Scan", &result);
    result
}

#[tauri::command]
pub async fn duplicates_apply(app: tauri::AppHandle, payload: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Duplicate Deletion", None);
    let json = serde_json::to_string(&payload)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let result = bridge()?.run_module("bridge_duplicates_apply", "", &[], Some(&json));
    emit_completion(&app, "Duplicate Deletion", &result);
    result
}

// ── Rename ──

#[tauri::command]
pub async fn rename_preview(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Rename Preview", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize rename options: {e}"))?;
    let (stdout_text, _stderr_text) = bridge()?.run_module_streaming(&app, "bridge_rename", "preview", &[], Some(&json))?;
    let result: Value = serde_json::from_str(stdout_text.trim())
        .map_err(|e| format!("Failed to parse rename result: {e}"))?;
    emit_completion(&app, "Rename Preview", &Ok(result.clone()));
    Ok(result)
}

#[tauri::command]
pub async fn rename_apply(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Rename Apply", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize rename options: {e}"))?;
    let result = bridge()?.run_module("bridge_rename", "apply", &[], Some(&json));
    emit_completion(&app, "Rename Apply", &result);
    result
}

// ── Trip ──

#[tauri::command]
pub async fn trip_preview(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Trip Preview", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let (stdout_text, _stderr_text) = bridge()?.run_module_streaming(&app, "bridge_trip", "preview", &[], Some(&json))?;
    let result: Value = serde_json::from_str(stdout_text.trim())
        .map_err(|e| format!("Failed to parse trip result: {e}"))?;
    emit_completion(&app, "Trip Preview", &Ok(result.clone()));
    Ok(result)
}

#[tauri::command]
pub async fn trip_apply(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Trip Apply", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let result = bridge()?.run_module("bridge_trip", "apply", &[], Some(&json));
    emit_completion(&app, "Trip Apply", &result);
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

#[tauri::command]
pub async fn review_apply_decisions(session_path: String, to_keep: Vec<Value>, to_remove: Vec<String>) -> Result<Value, String> {
    let json = serde_json::to_string(&serde_json::json!({
        "session_path": session_path,
        "to_keep": to_keep,
        "to_remove": to_remove,
    })).map_err(|e| format!("Serialize error: {e}"))?;
    bridge()?.run_module("bridge_review", "apply", &[], Some(&json))
}

// ── People ──

#[tauri::command]
pub async fn people_scan(app: tauri::AppHandle, config: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Face Scan", None);
    let json = serde_json::to_string(&config)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let (stdout_text, _stderr_text) = bridge()?.run_module_streaming(&app, "bridge_people", "scan", &[], Some(&json))?;
    let result: Value = serde_json::from_str(stdout_text.trim())
        .map_err(|e| format!("Failed to parse scan result: {e}"))?;
    emit_completion(&app, "Face Scan", &Ok(result.clone()));
    Ok(result)
}

#[tauri::command]
pub async fn people_scan_status(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_people", "status", &[], Some(&json))
}

#[tauri::command]
pub async fn people_scan_reset(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_people", "reset", &[], Some(&json))
}

#[tauri::command]
pub async fn people_catalog_list(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("{e}"))?;
    bridge()?.run_module("bridge_people", "catalog-list", &[], Some(&json))
}

#[tauri::command]
pub async fn people_person_rename(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("{e}"))?;
    bridge()?.run_module("bridge_people", "person-rename", &[], Some(&json))
}

#[tauri::command]
pub async fn people_person_create(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("{e}"))?;
    bridge()?.run_module("bridge_people", "person-create", &[], Some(&json))
}

#[tauri::command]
pub async fn people_person_reassign(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("{e}"))?;
    bridge()?.run_module("bridge_people", "person-reassign", &[], Some(&json))
}

#[tauri::command]
pub async fn people_person_merge(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_people", "person-merge", &[], Some(&json))
}

#[tauri::command]
pub async fn people_catalog_info(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Catalog Info", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let result = bridge()?.run_module("bridge_people", "catalog-info", &[], Some(&json));
    emit_completion(&app, "Catalog Info", &result);
    result
}

#[tauri::command]
pub async fn people_face_ignore(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_people", "face-ignore", &[], Some(&json))
}

#[tauri::command]
pub async fn people_face_age(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_people", "face-age", &[], Some(&json))
}

#[tauri::command]
pub async fn people_face_feedback(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_people", "face-feedback", &[], Some(&json))
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
pub async fn doctor_check(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Preflight Check", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let (stdout_text, _stderr_text) = bridge()?.run_module_streaming(&app, "bridge_doctor", "", &[], Some(&json))?;
    let result: Value = serde_json::from_str(stdout_text.trim())
        .map_err(|e| format!("Failed to parse doctor result: {e}"))?;
    emit_completion(&app, "Preflight Check", &Ok(result.clone()));
    Ok(result)
}

// ── Library ──

#[tauri::command]
pub async fn library_browse(_app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options).map_err(|e| format!("{e}"))?;
    bridge()?.run_module("bridge_library", "browse", &[], Some(&json))
}

// ── File Operations ──

#[tauri::command]
pub async fn file_open(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "open", &[], Some(&json))
}

#[tauri::command]
pub async fn file_reveal(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "reveal", &[], Some(&json))
}

#[tauri::command]
pub async fn file_delete(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "delete", &[], Some(&json))
}

#[tauri::command]
pub async fn file_rename(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "rename", &[], Some(&json))
}

#[tauri::command]
pub async fn file_export(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "export", &[], Some(&json))
}

#[tauri::command]
pub async fn file_integrity(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "integrity", &[], Some(&json))
}

#[tauri::command]
pub async fn file_backup(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "backup", &[], Some(&json))
}

#[tauri::command]
pub async fn file_contact_sheet(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "contact_sheet", &[], Some(&json))
}

#[tauri::command]
pub async fn file_web_gallery(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "web_gallery", &[], Some(&json))
}

#[tauri::command]
pub async fn file_watermark(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "watermark", &[], Some(&json))
}

#[tauri::command]
pub async fn file_batch_delete(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "batch_delete", &[], Some(&json))
}

#[tauri::command]
pub async fn file_batch_copy(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "batch_copy", &[], Some(&json))
}

#[tauri::command]
pub async fn file_thumbnail(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "thumbnail", &[], Some(&json))
}

#[tauri::command]
pub async fn file_thumbnails_batch(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "thumbnails_batch", &[], Some(&json))
}

#[tauri::command]
pub async fn file_watch_events(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_file_ops", "watch_events", &[], Some(&json))
}

#[tauri::command]
pub async fn read_thumbnails_batch(paths: Vec<String>) -> Result<Vec<String>, String> {
    use std::fs;
    use std::io::Read;

    let mut results = Vec::with_capacity(paths.len());

    for path in &paths {
        let mime = if path.to_lowercase().ends_with(".png") { "image/png" }
        else if path.to_lowercase().ends_with(".gif") { "image/gif" }
        else if path.to_lowercase().ends_with(".webp") { "image/webp" }
        else { "image/jpeg" };

        match fs::File::open(path) {
            Ok(file) => {
                let mut buf = Vec::new();
                if file.take(16 * 1024).read_to_end(&mut buf).is_ok() && !buf.is_empty() {
                    use base64::Engine;
                    let b64 = base64::engine::general_purpose::STANDARD.encode(&buf);
                    results.push(format!("data:{};base64,{}", mime, b64));
                } else {
                    results.push(String::new());
                }
            }
            Err(_) => {
                results.push(String::new());
            }
        }
    }

    Ok(results)
}

// ── Window ──

#[tauri::command]
pub async fn resize_window(app: tauri::AppHandle, width: u32, height: u32) -> Result<(), String> {
    let window = app.get_webview_window("main").ok_or("Window 'main' not found")?;
    window.set_size(tauri::Size::Physical(tauri::PhysicalSize { width, height }))
        .map_err(|e| format!("Failed to resize: {e}"))?;
    Ok(())
}

#[tauri::command]
pub async fn get_window_size(app: tauri::AppHandle) -> Result<(u32, u32), String> {
    let window = app.get_webview_window("main").ok_or("Window 'main' not found")?;
    let size = window.outer_size().map_err(|e| format!("Failed to get size: {e}"))?;
    Ok((size.width, size.height))
}

// ── Enrich ──

#[tauri::command]
pub async fn enrich_file(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_enrich", "enrich", &[], Some(&json))
}

#[tauri::command]
pub async fn enrich_batch(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_enrich", "enrich-batch", &[], Some(&json))
}

// ── Stats ──

#[tauri::command]
pub async fn library_stats(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Library Statistics", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let result = bridge()?.run_module("bridge_stats", "stats", &[], Some(&json));
    emit_completion(&app, "Library Statistics", &result);
    result
}

#[tauri::command]
pub async fn size_report(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Size Report", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let result = bridge()?.run_module("bridge_stats", "size-report", &[], Some(&json));
    emit_completion(&app, "Size Report", &result);
    result
}

// ── Search ──

#[tauri::command]
pub async fn media_search(app: tauri::AppHandle, options: Value) -> Result<Value, String> {
    emit_progress(&app, "operation:started", "Media Search", None);
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    let result = bridge()?.run_module("bridge_search", "search", &[], Some(&json));
    emit_completion(&app, "Media Search", &result);
    result
}

// ── Background Scan ──

#[tauri::command]
pub async fn background_scan(config: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&config)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_background", "check", &[], Some(&json))
}

// ── Groups ──

#[tauri::command]
pub async fn groups_by_date(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_groups", "group-by-date", &[], Some(&json))
}

#[tauri::command]
pub async fn groups_by_camera(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_groups", "group-by-camera", &[], Some(&json))
}

#[tauri::command]
pub async fn groups_by_location(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_groups", "group-by-location", &[], Some(&json))
}

#[tauri::command]
pub async fn groups_by_people(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_groups", "group-by-people", &[], Some(&json))
}

#[tauri::command]
pub async fn groups_timeline(options: Value) -> Result<Value, String> {
    let json = serde_json::to_string(&options)
        .map_err(|e| format!("Failed to serialize: {e}"))?;
    bridge()?.run_module("bridge_groups", "timeline", &[], Some(&json))
}
