import { useState, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import {
  FolderOpen,
  FolderSync,
  CopyX,
  Eye,
  Users,
  Clock,
  Settings,
  Plane,
  Workflow,
  Pencil,
  Info,
  Sun,
  Moon,
  Monitor,
  User,
  LayoutDashboard,
  Maximize2,
  Minimize2,
} from "lucide-react"
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useDashboardStore } from "@/stores/dashboard-store"
import { historyList, peopleCatalogList } from "@/lib/tauri-bridge"
import { DryRunToggle } from "@/components/shared/DryRunToggle"

interface SidebarItem {
  icon: React.ComponentType<any>
  label: string
  path: string
  tooltip: string
  visible: boolean
}

const defaultSidebarItems: Omit<SidebarItem, "visible">[] = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/", tooltip: "Overview and quick actions" },
  { icon: FolderOpen, label: "Library", path: "/library", tooltip: "Browse and manage your media library" },
  { icon: FolderSync, label: "Organize", path: "/organize", tooltip: "Auto-organize files into folders" },
  { icon: CopyX, label: "Duplicates", path: "/duplicates", tooltip: "Find and remove duplicate files" },
  { icon: Pencil, label: "Rename", path: "/rename", tooltip: "Batch rename media files" },
  { icon: Plane, label: "Trip", path: "/trip", tooltip: "Organize photos by trip / location" },
  { icon: Workflow, label: "Workflow", path: "/workflow", tooltip: "Create and run processing workflows" },
  { icon: Eye, label: "Review", path: "/review", tooltip: "Review flagged items before applying changes" },
  { icon: Users, label: "People", path: "/people", tooltip: "Manage detected faces and people" },
  { icon: User, label: "Face Timeline", path: "/face-timeline", tooltip: "Browse all photos of a person chronologically" },
  { icon: Clock, label: "History", path: "/history", tooltip: "View recent activity and undo actions" },
  { icon: Info, label: "About", path: "/about", tooltip: "About Media Manager" },
  { icon: Settings, label: "Settings", path: "/settings", tooltip: "Configure app preferences" },
]

const savedConfigKey = "sidebar_config"

export function AppSidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const lastScanStats = useDashboardStore((s) => s.lastScanStats)
  const [historyCount, setHistoryCount] = useState<number | null>(null)
  const [peopleCount, setPeopleCount] = useState<number | null>(null)
  const [currentTheme, setCurrentTheme] = useState<"light" | "dark" | "system">(() => {
    return (localStorage.getItem("theme") as "light" | "dark" | "system") || "system"
  })
  const [dryRun, setDryRun] = useState(() => localStorage.getItem("dry_run") === "true")

  const [sidebarItems, setSidebarItems] = useState<SidebarItem[]>(() => {
    const saved = localStorage.getItem(savedConfigKey)
    if (saved) {
      try {
        const config: Array<{ label: string; path: string; visible: boolean }> = JSON.parse(saved)
        return defaultSidebarItems.map(item => {
          const cfg = config.find((c) => c.path === item.path)
          return cfg ? { ...item, visible: cfg.visible ?? true } : { ...item, visible: true }
        })
      } catch { /* ignore corrupted config */ }
    }
    return defaultSidebarItems.map(item => ({ ...item, visible: true }))
  })

  const [showCustomize, setShowCustomize] = useState(false)

  const visibleItems = sidebarItems.filter(item => item.visible)

  const [isFullscreen, setIsFullscreen] = useState(false)

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const setTheme = (theme: "light" | "dark" | "system") => {
    setCurrentTheme(theme)
    localStorage.setItem("theme", theme)
    const root = document.documentElement
    if (theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      root.classList.add("dark")
    } else {
      root.classList.remove("dark")
    }
  }

  useEffect(() => {
    historyList()
      .then((h) => setHistoryCount(h.run_count))
      .catch(() => {})
  }, [])

  useEffect(() => {
    const catalogPath = localStorage.getItem("people_catalog_path")
    if (!catalogPath) return
    peopleCatalogList({ catalog_path: catalogPath })
      .then((c) => setPeopleCount(c.person_count))
      .catch(() => {})
  }, [])

  return (
    <Sidebar collapsible="icon" variant="sidebar">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              onClick={() => navigate("/about")}
              isActive={location.pathname === "/about"}
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary/70 text-primary-foreground">
                <span className="text-base inline-block hover:animate-bounce">📦</span>
              </div>
              <div className="flex flex-col gap-0.5 leading-none">
                <span className="font-semibold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  Media Manager
                </span>
                <span className="text-xs text-muted-foreground">v0.6.0</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {visibleItems.map((item) => {
                const isActive =
                  item.path === "/"
                    ? location.pathname === "/"
                    : location.pathname.startsWith(item.path)
                const badgeCount =
                  item.label === "Library" ? lastScanStats?.total_files ?? null
                  : item.label === "People" ? peopleCount
                  : item.label === "History" ? historyCount
                  : null
                return (
                  <SidebarMenuItem key={item.label}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <SidebarMenuButton
                          isActive={isActive}
                          onClick={() => navigate(item.path)}
                        >
                          <item.icon />
                          <span>{item.label}</span>
                          {badgeCount != null && (
                            <Badge variant="secondary" className="ml-auto text-[10px] px-1.5 py-0 h-4">{badgeCount}</Badge>
                          )}
                        </SidebarMenuButton>
                      </TooltipTrigger>
                      <TooltipContent side="right">
                        <p className="font-medium">{item.label}</p>
                        <p className="text-xs text-muted-foreground">{item.tooltip}</p>
                      </TooltipContent>
                    </Tooltip>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <div className="peer/menu-button group/menu-button flex w-full items-center gap-2 overflow-hidden rounded-md p-2 text-left text-sm outline-hidden transition-[width,height,padding]">
              <SidebarTrigger className="-ml-1" />
              <span className="group-data-[collapsible=icon]:hidden">
                Collapse
              </span>
            </div>
          </SidebarMenuItem>
        </SidebarMenu>
        {/* Theme toggle */}
        <div className="px-3 py-2">
          <div className="flex items-center justify-center gap-1 border rounded-lg p-1 bg-muted/30">
            {(["light", "dark", "system"] as const).map(theme => {
              const Icon = theme === "light" ? Sun : theme === "dark" ? Moon : Monitor
              const isActive = currentTheme === theme
              return (
                <button
                  key={theme}
                  onClick={() => setTheme(theme)}
                  className={`flex-1 flex items-center justify-center py-1.5 rounded-md transition-colors ${
                    isActive ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                  }`}
                  title={theme === "light" ? "Light" : theme === "dark" ? "Dark" : "System"}
                >
                  <Icon className="h-3.5 w-3.5" />
                </button>
              )
            })}
          </div>
        </div>
        {/* Dry-Run toggle */}
        <div className="px-3 pb-2">
          <DryRunToggle enabled={dryRun} onToggle={(v: boolean) => {
            setDryRun(v)
            localStorage.setItem("dry_run", String(v))
          }} />
        </div>

        {/* Fullscreen toggle */}
        <div className="px-3 pb-1">
          <button onClick={toggleFullscreen}
            className="flex items-center gap-1.5 text-[10px] text-muted-foreground hover:text-foreground px-1 py-1 w-full">
            {isFullscreen ? <Minimize2 className="h-3 w-3" /> : <Maximize2 className="h-3 w-3" />}
            {isFullscreen ? "Exit fullscreen" : "Fullscreen"}
          </button>
        </div>

        {/* Customize sidebar */}
        <div className="px-3 pb-2">
          <button onClick={() => setShowCustomize(true)}
            className="flex items-center gap-1.5 text-[10px] text-muted-foreground hover:text-foreground px-1 py-1 w-full">
            <Settings className="h-3 w-3" /> Customize sidebar
          </button>
        </div>

        {/* Customize dialog */}
        {showCustomize && (
          <div className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center" onClick={() => setShowCustomize(false)}>
            <div className="bg-background rounded-lg shadow-xl p-4 w-80 max-h-96 overflow-y-auto" onClick={e => e.stopPropagation()}>
              <h3 className="text-sm font-semibold mb-3">Customize Sidebar</h3>
              <p className="text-[10px] text-muted-foreground mb-3">Toggle visibility of sidebar items.</p>
              {sidebarItems.map((item, i) => (
                <label key={item.path} className="flex items-center gap-2 py-1.5 cursor-pointer hover:bg-muted/50 rounded px-1">
                  <input type="checkbox" checked={item.visible} onChange={() => {
                    const next = sidebarItems.map((s, j) => j === i ? {...s, visible: !s.visible} : s)
                    setSidebarItems(next)
                    localStorage.setItem(savedConfigKey, JSON.stringify(next.map(({label, path, visible}) => ({label, path, visible}))))
                  }} className="rounded" />
                  <item.icon className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="text-xs">{item.label}</span>
                </label>
              ))}
              <Button size="sm" className="mt-2 w-full" onClick={() => setShowCustomize(false)}>
                Done
              </Button>
            </div>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  )
}
