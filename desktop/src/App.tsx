import { useEffect, useState, Component, type ReactNode, lazy, Suspense } from "react"
import { useNavigate, useLocation, Outlet } from "react-router-dom"
import { useSettingsStore } from "@/stores/settings-store"
import { useT } from "@/lib/i18n"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"
import { AppSidebar } from "@/components/layout/AppSidebar"
import { ErrorBoundary } from "@/components/shared/ErrorBoundary"
import { WelcomeDialog } from "@/components/shared/WelcomeDialog"
import { OnboardingTour } from "@/components/shared/OnboardingTour"
import { ProgressOverlay } from "@/components/shared/ProgressOverlay"
import { MiniProgressOverlay } from "@/components/shared/MiniProgressOverlay"
import { ProgressProvider } from "@/lib/progress-context"

const CommandPalette = lazy(() => import("@/components/shared/CommandPalette").then(m => ({ default: m.CommandPalette })))
import { NotificationSystem } from "@/components/shared/NotificationSystem"
import { ToastContainer } from "@/components/shared/ToastContainer"
import { KeyboardShortcuts } from "@/components/shared/KeyboardShortcuts"

class AppErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex items-center justify-center min-h-screen p-8">
          <div className="text-center space-y-4 max-w-md">
            <h1 className="text-xl font-bold text-red-500">App Error</h1>
            <p className="text-sm text-muted-foreground">{this.state.error.message}</p>
            <button onClick={() => { this.setState({ error: null }); window.location.reload() }}
              className="px-4 py-2 bg-primary text-primary-foreground rounded">
              Reload App
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  const { settings, loaded: settingsLoaded, load: loadSettings } = useSettingsStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [showOnboardingTour, setShowOnboardingTour] = useState(false)
  const t = useT()
  const [dryRun] = useState(() => localStorage.getItem("dry_run") === "true")
  const [isFirstLaunch, setIsFirstLaunch] = useState(false)
  const [isTouchDevice, setIsTouchDevice] = useState(false)
  const [bridgeStatus, setBridgeStatus] = useState<"ok" | "error" | "checking">("checking")

  useEffect(() => {
    loadSettings()
  }, [])

  useEffect(() => {
    if (!settingsLoaded) return
    if (settings.show_onboarding && location.pathname !== "/onboarding") {
      navigate("/onboarding", { replace: true })
    }
  }, [settingsLoaded, settings?.show_onboarding, location.pathname])

  useEffect(() => {
    if (!settingsLoaded) return
    const completed = localStorage.getItem("onboarding_complete") === "true"
    if (!completed && !settings.show_onboarding && location.pathname !== "/onboarding") {
      setShowOnboardingTour(true)
    }
  }, [settingsLoaded, settings?.show_onboarding, location.pathname])

  useEffect(() => {
    const hasLaunched = localStorage.getItem("has_launched_before")
    if (!hasLaunched) {
      setIsFirstLaunch(true)
      localStorage.setItem("has_launched_before", "true")
    }
  }, [])

  useEffect(() => {
    import("@/lib/tauri-bridge").then(({ runtimeDiagnostics }) => {
      runtimeDiagnostics().then(() => setBridgeStatus("ok")).catch(() => setBridgeStatus("error"))
    })
  }, [])

  useEffect(() => { setIsTouchDevice("ontouchstart" in window) }, [])

  useEffect(() => { window.scrollTo(0, 0) }, [location.pathname])

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return

      if (e.ctrlKey) {
        switch (e.key) {
          case "1": e.preventDefault(); navigate("/"); break
          case "2": e.preventDefault(); navigate("/library"); break
          case "3": e.preventDefault(); navigate("/organize"); break
          case "4": e.preventDefault(); navigate("/duplicates"); break
          case "5": e.preventDefault(); navigate("/people"); break
          case ",": e.preventDefault(); navigate("/settings"); break
        }
        return
      }

      if (e.key === "?") {
        e.preventDefault()
        setShortcutsOpen(true)
      }
      if (e.key === "F11") {
        e.preventDefault()
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen()
        } else {
          document.exitFullscreen()
        }
      }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [navigate])

  return (
    <ProgressProvider>
      <TooltipProvider delayDuration={isTouchDevice ? 999999 : 600} skipDelayDuration={200}>
        <SidebarProvider>
          <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded">
            Skip to main content
          </a>
          <div id="announcements" className="sr-only" aria-live="polite" aria-atomic="true" />
          <AppSidebar />
          <SidebarInset>
            <ErrorBoundary>
              {dryRun && (
                <div className="bg-amber-100 dark:bg-amber-900/30 border-b border-amber-300 dark:border-amber-700 px-4 py-1.5 text-center text-xs text-amber-800 dark:text-amber-300">
                  {t("\u26A0\uFE0F DRY-RUN MODE ACTIVE \u2014 No files will be modified. Disable in sidebar.",
                     "\u26A0\uFE0F DRY-RUN-MODUS AKTIV \u2014 Keine Dateien werden ver\u00E4ndert. In der Sidebar deaktivieren.")}
                </div>
              )}
              <div key={location.pathname} className="page-enter" id="main-content">
                <AppErrorBoundary>
                  <Outlet />
                </AppErrorBoundary>
              </div>
            </ErrorBoundary>
          </SidebarInset>
        </SidebarProvider>
        <ProgressOverlay />
        <Suspense fallback={null}>
        <CommandPalette />
        </Suspense>
        <NotificationSystem />
        <ToastContainer />
        <KeyboardShortcuts open={shortcutsOpen} onOpenChange={setShortcutsOpen} />
      </TooltipProvider>
      <MiniProgressOverlay />
      {bridgeStatus === "error" && (
        <div className="fixed bottom-4 left-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm">
          Python engine not reachable. Some features unavailable.
        </div>
      )}
      {isFirstLaunch && <WelcomeDialog open={isFirstLaunch} onClose={() => setIsFirstLaunch(false)} />}
      {showOnboardingTour && (
        <OnboardingTour onClose={() => setShowOnboardingTour(false)} />
      )}
    </ProgressProvider>
  )
}

export default App
