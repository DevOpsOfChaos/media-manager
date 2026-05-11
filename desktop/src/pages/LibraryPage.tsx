import { PageHeader } from "@/components/layout/PageHeader"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function LibraryPage() {
  return (
    <>
      <PageHeader title="Library">
        <Badge variant="secondary" className="text-xs">
          0 items
        </Badge>
      </PageHeader>
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
              <p className="text-sm text-muted-foreground">
                Library browser will be implemented in the next phase.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}
