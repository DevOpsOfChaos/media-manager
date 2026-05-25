import { useEffect } from "react"
import { useNavigate, useLocation, Outlet } from "react-router-dom"
import { useSettingsStore } from "@/stores/settings-store"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"
import { AppSidebar } from "@/components/layout/AppSidebar"
import { ErrorBoundary } from "@/components/shared/ErrorBoundary"
import { ProgressOverlay } from "@/components/shared/ProgressOverlay"
import { CommandPalette } from "@/components/shared/CommandPalette"
import { NotificationSystem } from "@/components/shared/NotificationSystem"

function App() {
  const { settings, loaded: settingsLoaded, load: loadSettings } = useSettingsStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    loadSettings()
  }, [])

  useEffect(() => {
    if (!settingsLoaded) return
    if (settings.show_onboarding && location.pathname !== "/onboarding") {
      navigate("/onboarding", { replace: true })
    }
  }, [settingsLoaded, settings?.show_onboarding, location.pathname])

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <ErrorBoundary><Outlet /></ErrorBoundary>
        </SidebarInset>
      </SidebarProvider>
      <ProgressOverlay />
      <CommandPalette />
      <NotificationSystem />
    </TooltipProvider>
  )
}

export default App
