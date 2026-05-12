import { useNavigate } from "react-router-dom"
import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/shared/EmptyState"

export default function LibraryPage() {
  const navigate = useNavigate()

  return (
    <>
      <PageHeader title="Library" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          <EmptyState
            title="Library browser not yet connected"
            description="The media library browser will be available in a future update. For now, use Organize Preview to see how files would be structured, or browse History to inspect past runs."
            action={
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate("/organize")}
                >
                  Open Organize
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate("/history")}
                >
                  Open History
                </Button>
              </div>
            }
          />

          <Card>
            <CardHeader>
              <CardTitle>Quick actions</CardTitle>
              <CardDescription>
                Tools available in the current version.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-3">
              <button
                onClick={() => navigate("/organize")}
                className="rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
              >
                <p className="text-sm font-medium">Organize Preview</p>
                <p className="text-xs text-muted-foreground">
                  Preview folder organization.
                </p>
              </button>
              <button
                onClick={() => navigate("/duplicates")}
                className="rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
              >
                <p className="text-sm font-medium">Duplicates</p>
                <p className="text-xs text-muted-foreground">
                  Scan for duplicate files.
                </p>
              </button>
              <button
                onClick={() => navigate("/history")}
                className="rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
              >
                <p className="text-sm font-medium">History</p>
                <p className="text-xs text-muted-foreground">
                  Browse past runs.
                </p>
              </button>
              <button
                onClick={() => navigate("/settings")}
                className="rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
              >
                <p className="text-sm font-medium">Settings</p>
                <p className="text-xs text-muted-foreground">
                  Configure the app.
                </p>
              </button>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}
