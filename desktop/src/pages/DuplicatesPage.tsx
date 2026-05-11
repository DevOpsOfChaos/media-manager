import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function DuplicatesPage() {
  return (
    <>
      <PageHeader title="Duplicates" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Find Duplicates</CardTitle>
              <CardDescription>
                Scan for exact duplicates and similar images, then clean them
                up.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Duplicate scanner will be implemented in the next phase.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}
