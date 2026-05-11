import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function HistoryPage() {
  return (
    <>
      <PageHeader title="History" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Run History</CardTitle>
              <CardDescription>
                Browse past runs, inspect results, and undo operations.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Run history will be implemented in the next phase.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}
