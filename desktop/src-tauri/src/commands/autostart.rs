use std::path::PathBuf;

#[tauri::command]
pub fn get_autostart_status() -> Result<bool, String> {
    let exe_path = std::env::current_exe().map_err(|e| e.to_string())?;
    let exe_name = exe_path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("media-manager");
    let startup_dir = get_startup_folder()?;
    let shortcut_path = startup_dir.join(format!("{exe_name}.lnk"));
    Ok(shortcut_path.exists())
}

#[tauri::command]
pub fn set_autostart(enable: bool) -> Result<(), String> {
    let exe_path = std::env::current_exe().map_err(|e| e.to_string())?;
    let exe_name = exe_path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("media-manager");
    let startup_dir = get_startup_folder()?;
    let shortcut_path = startup_dir.join(format!("{exe_name}.lnk"));

    if enable {
        #[cfg(target_os = "windows")]
        {
            std::process::Command::new("powershell")
                .args([
                    "-Command",
                    &format!(
                        "$WshShell = New-Object -ComObject WScript.Shell; \
                         $Shortcut = $WshShell.CreateShortcut('{}'); \
                         $Shortcut.TargetPath = '{}'; \
                         $Shortcut.Arguments = '--background'; \
                         $Shortcut.WorkingDirectory = '{}'; \
                         $Shortcut.Save()",
                        shortcut_path.display(),
                        exe_path.display(),
                        exe_path.parent().unwrap_or(&std::path::PathBuf::from(".")).display(),
                    ),
                ])
                .output()
                .map_err(|e| format!("Failed to create shortcut: {e}"))?;
        }
        Ok(())
    } else {
        if shortcut_path.exists() {
            std::fs::remove_file(&shortcut_path)
                .map_err(|e| format!("Failed to remove: {e}"))?;
        }
        Ok(())
    }
}

#[cfg(target_os = "windows")]
fn get_startup_folder() -> Result<PathBuf, String> {
    Ok(PathBuf::from(
        std::env::var("APPDATA").map_err(|e| e.to_string())?,
    )
    .join("Microsoft")
    .join("Windows")
    .join("Start Menu")
    .join("Programs")
    .join("Startup"))
}

#[cfg(not(target_os = "windows"))]
fn get_startup_folder() -> Result<PathBuf, String> {
    Err("Auto-start only supported on Windows".to_string())
}
