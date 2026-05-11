import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  SidebarFooter,
} from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { TooltipProvider } from "@/components/ui/tooltip"
import {
  FolderOpen,
  Library,
  Settings,
  Activity,
  Layers,
  FileText,
  PanelRight,
} from "lucide-react"

const navItems = [
  { icon: Library, label: "Library", active: true },
  { icon: FolderOpen, label: "Browse", active: false },
  { icon: Layers, label: "Collections", active: false },
  { icon: Activity, label: "Activity", active: false },
  { icon: FileText, label: "Reports", active: false },
  { icon: Settings, label: "Settings", active: false },
]

function App() {
  return (
    <TooltipProvider>
      <SidebarProvider>
        <Sidebar collapsible="icon" variant="sidebar">
          <SidebarHeader>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton size="lg">
                  <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                    <Library className="size-4" />
                  </div>
                  <div className="flex flex-col gap-0.5 leading-none">
                    <span className="font-semibold">Media Manager</span>
                    <span className="text-xs text-muted-foreground">
                      v0.1.0
                    </span>
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
                  {navItems.map((item) => (
                    <SidebarMenuItem key={item.label}>
                      <SidebarMenuButton
                        isActive={item.active}
                        tooltip={item.label}
                      >
                        <item.icon />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
          <SidebarFooter>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton tooltip="Toggle sidebar">
                  <SidebarTrigger className="-ml-1" />
                  <span>Collapse</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarFooter>
        </Sidebar>

        <SidebarInset>
          <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <div className="flex flex-1 items-center gap-2">
              <h2 className="text-sm font-medium">Library</h2>
              <Badge variant="secondary" className="text-xs">
                1,234 items
              </Badge>
            </div>
          </header>

          <main className="flex flex-1 gap-4 p-4">
            <div className="flex-1">
              <Card>
                <CardHeader>
                  <CardTitle>Files</CardTitle>
                  <CardDescription>
                    Browse and manage your media library.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] rounded-md">
                    <div className="grid grid-cols-4 gap-3 pr-4">
                      {Array.from({ length: 12 }).map((_, i) => (
                        <div
                          key={i}
                          className="flex aspect-square items-center justify-center rounded-lg border bg-muted/30 text-sm text-muted-foreground"
                        >
                          Item {i + 1}
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>

            <aside className="w-72 shrink-0">
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <PanelRight className="size-4 text-muted-foreground" />
                    <CardTitle className="text-sm">Details</CardTitle>
                  </div>
                  <CardDescription>
                    Select an item to view details.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">
                      Name
                    </p>
                    <p className="text-sm">No selection</p>
                  </div>
                  <Separator />
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">
                      Path
                    </p>
                    <p className="text-sm text-muted-foreground">—</p>
                  </div>
                  <Separator />
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">
                      Size
                    </p>
                    <p className="text-sm text-muted-foreground">—</p>
                  </div>
                  <Separator />
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">
                      Modified
                    </p>
                    <p className="text-sm text-muted-foreground">—</p>
                  </div>
                </CardContent>
              </Card>
            </aside>
          </main>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  )
}

export default App
