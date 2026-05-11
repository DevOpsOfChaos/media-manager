import { useEffect } from "react"
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

  useEffect(() => {
    load()
  }, [load])

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
        </div>
      </main>
    </>
  )
}
