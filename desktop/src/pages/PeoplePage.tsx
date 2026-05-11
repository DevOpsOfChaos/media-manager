import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function PeoplePage() {
  return (
    <>
      <PageHeader title="People" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Face Recognition</CardTitle>
              <CardDescription>
                Scan for faces, review unknown people, and manage your people
                catalog.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                People recognition will be implemented in the next phase.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}
