use serde_json::Value;
use std::collections::HashMap;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::OnceLock;

/// Hardened Python discovery, env setup, and subprocess execution for
/// calling `python -m media_manager.<module>` from Tauri commands.
#[derive(Debug)]
pub struct PythonBridge {
    executable: String,
    project_root: PathBuf,
    settings_path: Option<String>,
}

impl PythonBridge {
    /// Resolve the singleton bridge config.
    ///
    /// Order of precedence for Python executable:
    ///   1. `MEDIA_MANAGER_PYTHON` env var (absolute path)
    ///   2. `VIRTUAL_ENV` → `$VIRTUAL_ENV/Scripts/python.exe` (Windows)
    ///   3. `CONDA_PREFIX` → `$CONDA_PREFIX/python.exe` (Windows)
    ///   4. `python`, `python3` from PATH
    ///
    /// Order for project root (used as working dir + `PYTHONPATH` base):
    ///   1. `MEDIA_MANAGER_PROJECT_ROOT` env var
    ///   2. Compile-time `CARGO_MANIFEST_DIR/../..` (dev fallback)
    ///
    /// Order for settings path:
    ///   1. `MEDIA_MANAGER_SETTINGS_PATH` env var
    ///   2. `None` — Python uses its own default
    pub fn get() -> &'static Result<PythonBridge, String> {
        static INSTANCE: OnceLock<Result<PythonBridge, String>> = OnceLock::new();
        INSTANCE.get_or_init(Self::resolve)
    }

    fn resolve() -> Result<PythonBridge, String> {
        let executable = find_python()?;
        let project_root = resolve_project_root()?;
        let settings_path = std::env::var("MEDIA_MANAGER_SETTINGS_PATH").ok();

        Ok(PythonBridge {
            executable,
            project_root,
            settings_path,
        })
    }

    // ── accessors for diagnostics ──

    pub fn executable(&self) -> &str {
        &self.executable
    }

    pub fn project_root(&self) -> &Path {
        &self.project_root
    }

    pub fn settings_path(&self) -> Option<&str> {
        self.settings_path.as_deref()
    }

    /// Compute the PYTHONPATH that would be used for subprocess calls.
    pub fn effective_pythonpath(&self) -> String {
        let src_dir = self.project_root.join("src");
        let separator = if cfg!(windows) { ";" } else { ":" };
        let existing = std::env::var("PYTHONPATH").unwrap_or_default();
        if existing.is_empty() {
            src_dir.to_string_lossy().to_string()
        } else {
            format!("{}{separator}{existing}", src_dir.display())
        }
    }

    /// Run a Python bridge module with the given action and optional extra args.
    ///
    /// - `module`: the dotted module name under `media_manager` (e.g. `bridge_settings`)
    /// - `action`: the first CLI argument (e.g. `read`, `write`, `reset`)
    /// - `extra_args`: additional arguments appended after the action
    /// - `stdin_json`: optional JSON string to pipe to stdin
    pub fn run_module(
        &self,
        module: &str,
        action: &str,
        extra_args: &[&str],
        stdin_json: Option<&str>,
    ) -> Result<Value, String> {
        let full_module = format!("media_manager.{module}");
        let src_dir = self.project_root.join("src");

        // Build augmented environment
        let mut env_vars: HashMap<String, String> =
            std::env::vars().collect();

        // Prepend src/ to PYTHONPATH so `media_manager` is importable
        let separator = if cfg!(windows) { ";" } else { ":" };
        let existing = env_vars.get("PYTHONPATH").cloned().unwrap_or_default();
        let new_pythonpath = if existing.is_empty() {
            src_dir.to_string_lossy().to_string()
        } else {
            format!("{}{separator}{existing}", src_dir.display())
        };
        env_vars.insert("PYTHONPATH".into(), new_pythonpath);

        if let Some(ref sp) = self.settings_path {
            env_vars.insert("MEDIA_MANAGER_SETTINGS_PATH".into(), sp.clone());
        }

        // Build args list: -m <module> <action> [extra_args...]
        let mut args: Vec<String> = vec![
            "-m".into(),
            full_module,
            action.into(),
        ];
        for a in extra_args {
            args.push(a.to_string());
        }

        // Pass --settings-path if bridge supports it and we have an override
        if let Some(ref sp) = self.settings_path {
            args.push("--settings-path".into());
            args.push(sp.clone());
        }

        let mut child = Command::new(&self.executable)
            .args(&args)
            .current_dir(&self.project_root)
            .env_clear()
            .envs(&env_vars)
            .stdin(if stdin_json.is_some() {
                Stdio::piped()
            } else {
                Stdio::null()
            })
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| {
                format!(
                    "Failed to spawn Python ({}): {e}\n\
                     Project root: {}\n\
                     Hint: Set MEDIA_MANAGER_PYTHON to the correct python executable.",
                    self.executable,
                    self.project_root.display(),
                )
            })?;

        // Write stdin if provided
        if let Some(input) = stdin_json {
            if let Some(mut stdin) = child.stdin.take() {
                stdin
                    .write_all(input.as_bytes())
                    .map_err(|e| format!("Failed to write stdin: {e}"))?;
            }
        }

        let output = child
            .wait_with_output()
            .map_err(|e| format!("Python process error: {e}"))?;

        let stderr_text = String::from_utf8_lossy(&output.stderr)
            .trim()
            .to_string();

        if !output.status.success() {
            let detail = if stderr_text.is_empty() {
                format!("exit code {}", output.status.code().unwrap_or(-1))
            } else {
                // Try to extract the JSON error from stderr
                if let Ok(err_val) = serde_json::from_str::<Value>(&stderr_text) {
                    err_val
                        .get("error")
                        .and_then(|v| v.as_str())
                        .unwrap_or(&stderr_text)
                        .to_string()
                } else {
                    stderr_text
                }
            };
            return Err(format!(
                "Python bridge error ({module} {action}): {detail}"
            ));
        }

        let stdout_text = String::from_utf8_lossy(&output.stdout);
        let trimmed = stdout_text.trim();
        if trimmed.is_empty() {
            return Err(format!(
                "Python bridge returned empty output ({module} {action})."
            ));
        }

        serde_json::from_str(trimmed).map_err(|e| {
            let preview: String = trimmed
                .chars()
                .take(300)
                .collect();
            format!(
                "Failed to parse Python bridge output as JSON ({module} {action}): {e}\n\
                 Raw output (first 300 chars): {preview}"
            )
        })
    }
}

// ── Python discovery ──

fn find_python() -> Result<String, String> {
    // 1. Explicit override
    if let Ok(path) = std::env::var("MEDIA_MANAGER_PYTHON") {
        let p = Path::new(&path);
        if p.is_file() || p.with_extension("exe").is_file() {
            return Ok(path);
        }
        // Try the path as-is even if not found — user knows best
        return Ok(path);
    }

    // 2. Virtual environment
    if let Ok(venv) = std::env::var("VIRTUAL_ENV") {
        let venv_python = if cfg!(windows) {
            Path::new(&venv).join("Scripts").join("python.exe")
        } else {
            Path::new(&venv).join("bin").join("python")
        };
        if venv_python.is_file() {
            return Ok(venv_python.to_string_lossy().to_string());
        }
    }

    // 3. Conda
    if let Ok(conda_prefix) = std::env::var("CONDA_PREFIX") {
        let conda_python = if cfg!(windows) {
            Path::new(&conda_prefix).join("python.exe")
        } else {
            Path::new(&conda_prefix).join("bin").join("python")
        };
        if conda_python.is_file() {
            return Ok(conda_python.to_string_lossy().to_string());
        }
    }

    // 4. Fall back to PATH
    for candidate in &["python", "python3"] {
        if Command::new(candidate)
            .arg("--version")
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok()
        {
            return Ok(candidate.to_string());
        }
    }

    Err(
        "Python not found.\n\
         Tried: MEDIA_MANAGER_PYTHON env, VIRTUAL_ENV, CONDA_PREFIX, python, python3.\n\
         Set MEDIA_MANAGER_PYTHON to the python executable path."
            .into(),
    )
}

fn resolve_project_root() -> Result<PathBuf, String> {
    // 1. Explicit override
    if let Ok(root) = std::env::var("MEDIA_MANAGER_PROJECT_ROOT") {
        let p = Path::new(&root);
        if p.is_dir() {
            return Ok(p.to_path_buf());
        }
    }

    // 2. Compile-time fallback: CARGO_MANIFEST_DIR is desktop/src-tauri/
    //    so parent is src-tauri/, parent.parent is desktop/, parent.parent.parent is repo root
    let manifest_dir = Path::new(env!("CARGO_MANIFEST_DIR"));
    // desktop/src-tauri → repo root (two levels up)
    let candidate = manifest_dir
        .parent() // src-tauri
        .and_then(|p| p.parent()) // desktop
        .and_then(|p| p.parent()); // repo root

    if let Some(root) = candidate {
        if root.join("src").join("media_manager").is_dir() {
            return Ok(root.to_path_buf());
        }
    }

    // 3. Walk up from current dir looking for pyproject.toml
    if let Ok(cwd) = std::env::current_dir() {
        let mut current = cwd.as_path();
        for _ in 0..6 {
            if current.join("pyproject.toml").is_file()
                && current.join("src").join("media_manager").is_dir()
            {
                return Ok(current.to_path_buf());
            }
            if let Some(parent) = current.parent() {
                current = parent;
            } else {
                break;
            }
        }
    }

    Err(format!(
        "Could not resolve project root.\n\
         Set MEDIA_MANAGER_PROJECT_ROOT to the repository root (contains src/media_manager/).\n\
         Compile-time manifest: {}",
        env!("CARGO_MANIFEST_DIR")
    ))
}

// ── tests ──

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_find_python_returns_something() {
        // In dev, we should always find at least one python
        let result = find_python();
        assert!(
            result.is_ok(),
            "find_python() failed: {result:?}. Set MEDIA_MANAGER_PYTHON if needed."
        );
    }

    #[test]
    fn test_find_python_respects_env_override() {
        // Safety: save and restore the env var
        let saved = std::env::var("MEDIA_MANAGER_PYTHON").ok();
        std::env::set_var("MEDIA_MANAGER_PYTHON", "nonexistent-python-test");
        let result = find_python();
        assert_eq!(result.unwrap(), "nonexistent-python-test");
        // Restore
        match saved {
            Some(v) => std::env::set_var("MEDIA_MANAGER_PYTHON", v),
            None => std::env::remove_var("MEDIA_MANAGER_PYTHON"),
        }
    }

    #[test]
    fn test_resolve_project_root_finds_repo() {
        let result = resolve_project_root();
        assert!(
            result.is_ok(),
            "resolve_project_root() failed: {result:?}"
        );
        let root = result.unwrap();
        assert!(
            root.join("src").join("media_manager").is_dir(),
            "Resolved root {root:?} does not contain src/media_manager/"
        );
    }

    #[test]
    fn test_bridge_config_resolves() {
        let result = PythonBridge::resolve();
        assert!(result.is_ok(), "PythonBridge::resolve() failed: {result:?}");
    }

    #[test]
    fn test_diagnostics_accessors() {
        let result = PythonBridge::resolve();
        assert!(result.is_ok(), "PythonBridge::resolve() failed: {result:?}");
        let bridge = result.unwrap();

        let exe = bridge.executable();
        assert!(!exe.is_empty(), "executable should not be empty");

        let root = bridge.project_root();
        assert!(
            root.join("src").join("media_manager").is_dir(),
            "project_root should contain src/media_manager/"
        );

        let pp = bridge.effective_pythonpath();
        assert!(!pp.is_empty(), "effective_pythonpath should not be empty");
        assert!(
            pp.contains("src"),
            "PYTHONPATH should contain src/: {pp}"
        );
    }
}
