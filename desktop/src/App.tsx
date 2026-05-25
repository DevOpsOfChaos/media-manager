import { useEffect } from "react"
import { useNavigate, useLocation, Outlet } from "react-router-dom"
import { useSettingsStore } from "@/stores/settings-store"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"
import { AppSidebar } from "@/components/layout/AppSidebar"
import { ErrorBoundary } from "@/components/shared/ErrorBoundary"
import { ProgressOverlay } from "@/components/shared/ProgressOverlay"

function App() {
  const { settings, load: loadSettings } = useSettingsStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    loadSettings()
  }, [])

  useEffect(() => {
    if (settings && settings.show_onboarding && location.pathname !== "/onboarding") {
      navigate("/onboarding", { replace: true })
    }
  }, [settings, location.pathname])

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <ErrorBoundary><Outlet /></ErrorBoundary>
        </SidebarInset>
      </SidebarProvider>
      <ProgressOverlay />
    </TooltipProvider>
  )
}

export default App
