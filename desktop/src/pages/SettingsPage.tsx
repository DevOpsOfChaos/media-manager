import { useCallback, useEffect, useState } from "react"
import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useSettingsStore } from "@/stores/settings-store"
import {
  runtimeDiagnostics,
  type RuntimeDiagnostics,
} from "@/lib/tauri-bridge"
import type { Language, Theme } from "@/types"

export default function SettingsPage() {
  const {
    settings,
    loading,
    error,
    dirty,
    saved,
    updateSettings,
    load,
    save,
    reset,
  } = useSettingsStore()

  const [diag, setDiag] = useState<RuntimeDiagnostics | null>(null)
  const [diagLoading, setDiagLoading] = useState(false)
  const [diagError, setDiagError] = useState<string | null>(null)
  const [diagOpen, setDiagOpen] = useState(false)

  useEffect(() => {
    load()
  }, [load])

  const runDiag = useCallback(async () => {
    setDiagLoading(true)
    setDiagError(null)
    try {
      const result = await runtimeDiagnostics()
      setDiag(result)
    } catch (err) {
      setDiagError(String(err))
    } finally {
      setDiagLoading(false)
    }
  }, [])

  const pythonOk = diag?.python_reachable === true

  return (
    <>
      <PageHeader title="Settings" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-2xl space-y-4">
          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}
          {saved && (
            <div className="rounded-lg border border-green-500/50 bg-green-500/10 px-4 py-3 text-sm text-green-600 dark:text-green-400">
              Settings saved successfully.
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>General</CardTitle>
              <CardDescription>
                Language, theme, and startup preferences.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Language</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.language}
                  onChange={(e) =>
                    updateSettings({ language: e.target.value as Language })
                  }
                >
                  <option value="en">English</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Theme</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.theme}
                  onChange={(e) =>
                    updateSettings({ theme: e.target.value as Theme })
                  }
                >
                  <option value="modern-dark">Dark</option>
                  <option value="modern-light">Light</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Start Page</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.start_page_id}
                  onChange={(e) =>
                    updateSettings({ start_page_id: e.target.value })
                  }
                >
                  <option value="dashboard">Dashboard</option>
                  <option value="library">Library</option>
                  <option value="organize">Organize</option>
                  <option value="duplicates">Duplicates</option>
                  <option value="people">People</option>
                  <option value="history">History</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Behavior</CardTitle>
              <CardDescription>
                Confirmation dialogs, onboarding, and power-user features.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-input"
                  checked={settings.confirm_before_apply}
                  onChange={(e) =>
                    updateSettings({ confirm_before_apply: e.target.checked })
                  }
                />
                <span className="text-sm">
                  Confirm before applying changes to files
                </span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-input"
                  checked={settings.enable_command_palette}
                  onChange={(e) =>
                    updateSettings({ enable_command_palette: e.target.checked })
                  }
                />
                <span className="text-sm">Enable command palette (Ctrl+K)</span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-input"
                  checked={settings.show_onboarding}
                  onChange={(e) =>
                    updateSettings({ show_onboarding: e.target.checked })
                  }
                />
                <span className="text-sm">Show onboarding for new users</span>
              </label>
            </CardContent>
          </Card>

          <div className="flex items-center gap-3">
            <Button onClick={save} disabled={loading || !dirty}>
              {loading ? "Saving..." : "Save"}
            </Button>
            <Button variant="outline" onClick={reset} disabled={loading}>
              Reset to defaults
            </Button>
            {dirty && (
              <span className="text-xs text-muted-foreground">
                Unsaved changes
              </span>
            )}
          </div>

          {/* ── Diagnostics ── */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setDiagOpen(!diagOpen)}
                  className="text-left"
                >
                  <CardTitle>Runtime Diagnostics</CardTitle>
                  <CardDescription>
                    Python bridge health and environment information.
                  </CardDescription>
                </button>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setDiagOpen(true)
                      runDiag()
                    }}
                    disabled={diagLoading}
                  >
                    {diagLoading ? "Checking..." : "Refresh"}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDiagOpen(!diagOpen)}
                  >
                    {diagOpen ? "Hide" : "Show"}
                  </Button>
                </div>
              </div>
            </CardHeader>
            {diagOpen && (
              <CardContent>
                {diagError && (
                  <div className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive mb-3">
                    {diagError}
                  </div>
                )}

                {diag ? (
                  <div className="space-y-3 text-sm">
                    <StatusRow
                      label="Python Reachable"
                      ok={pythonOk}
                      detail={diag.python_error}
                    />
                    <StatusRow
                      label="media_manager import"
                      ok={diag.media_manager_import?.ok}
                      detail={diag.media_manager_import?.error}
                    />
                    <StatusRow
                      label="bridge_settings import"
                      ok={diag.bridge_settings_import?.ok}
                      detail={diag.bridge_settings_import?.error}
                    />
                    <StatusRow
                      label="Settings file"
                      ok={diag.settings_file_exists}
                      detail={
                        diag.settings_file_exists
                          ? diag.settings_path
                          : `Not found: ${diag.settings_path}`
                      }
                    />

                    <Separator />

                    <InfoRow label="Python executable" value={diag.python_exe} />
                    <InfoRow
                      label="Python version"
                      value={diag.python_version ?? "—"}
                    />
                    <InfoRow label="Project root" value={diag.project_root} />
                    <InfoRow
                      label="PYTHONPATH"
                      value={diag.pythonpath_prepended || "—"}
                    />
                    {diag.settings_path_override && (
                      <InfoRow
                        label="Settings path override"
                        value={diag.settings_path_override}
                      />
                    )}

                    <Separator />

                    <p className="text-xs font-medium text-muted-foreground">
                      Environment Hints
                    </p>
                    <div className="grid grid-cols-2 gap-1 text-xs text-muted-foreground">
                      <EnvHint
                        label="MEDIA_MANAGER_PYTHON"
                        value={diag.env_hints.MEDIA_MANAGER_PYTHON}
                      />
                      <EnvHint
                        label="VIRTUAL_ENV"
                        value={diag.env_hints.VIRTUAL_ENV}
                      />
                      <EnvHint
                        label="CONDA_PREFIX"
                        value={diag.env_hints.CONDA_PREFIX}
                      />
                      <EnvHint
                        label="PROJECT_ROOT"
                        value={diag.env_hints.MEDIA_MANAGER_PROJECT_ROOT}
                      />
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Click Refresh to check Python bridge health.
                  </p>
                )}
              </CardContent>
            )}
          </Card>
        </div>
      </main>
    </>
  )
}

function StatusRow({
  label,
  ok,
  detail,
}: {
  label: string
  ok?: boolean
  detail?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex size-2 shrink-0 rounded-full ${
          ok ? "bg-green-500" : "bg-destructive"
        }`}
      />
      <span className="font-medium">{label}</span>
      {detail && (
        <span className="truncate text-xs text-muted-foreground">
          {detail}
        </span>
      )}
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="truncate font-mono text-xs">{value}</span>
    </div>
  )
}

function EnvHint({
  label,
  value,
}: {
  label: string
  value: string | null | undefined
}) {
  return (
    <div className="flex items-center gap-1.5">
      <span
        className={`inline-flex size-1.5 rounded-full ${
          value ? "bg-green-500" : "bg-muted-foreground/30"
        }`}
      />
      <span className="truncate">
        {label}={value ? "set" : "—"}
      </span>
    </div>
  )
}

function Separator() {
  return <div className="border-t" />
}
