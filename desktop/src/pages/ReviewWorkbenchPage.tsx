import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { EmptyState } from "@/components/shared/EmptyState"

export default function ReviewWorkbenchPage() {
  return (
    <>
      <PageHeader title="Review" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
            Preview only. No files are deleted or modified. The Review
            Workbench will be available in a future update.
          </div>

          <EmptyState
            title="Review Workbench not connected yet"
            description="The Review Workbench will help you review duplicate groups and similar image candidates, record keep/remove decisions, and later apply them with journal and undo safeguards."
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Card className="opacity-60">
              <CardHeader>
                <CardTitle className="text-sm">Exact duplicates</CardTitle>
                <CardDescription className="text-xs">
                  Review byte-identical files and decide which to keep.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">Not available yet</p>
              </CardContent>
            </Card>

            <Card className="opacity-60">
              <CardHeader>
                <CardTitle className="text-sm">Similar images</CardTitle>
                <CardDescription className="text-xs">
                  Review visually similar images and compare candidates.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">Not available yet</p>
              </CardContent>
            </Card>

            <Card className="opacity-60">
              <CardHeader>
                <CardTitle className="text-sm">Decision journal</CardTitle>
                <CardDescription className="text-xs">
                  Record keep/remove decisions and apply later with undo.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">Not available yet</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </>
  )
}
