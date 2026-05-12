import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { EmptyState } from "@/components/shared/EmptyState"

export default function PeoplePage() {
  return (
    <>
      <PageHeader title="People" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          <EmptyState
            title="People recognition not yet available"
            description="Face recognition and people cataloging will be added in a future update. This feature will scan photos for faces and help you organize by person."
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Card className="opacity-60">
              <CardHeader>
                <CardTitle className="text-sm">Face detection</CardTitle>
                <CardDescription className="text-xs">
                  Automatic face detection in photos and videos.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Not available yet
                </p>
              </CardContent>
            </Card>

            <Card className="opacity-60">
              <CardHeader>
                <CardTitle className="text-sm">Face clustering</CardTitle>
                <CardDescription className="text-xs">
                  Group similar faces across your library.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Not available yet
                </p>
              </CardContent>
            </Card>

            <Card className="opacity-60">
              <CardHeader>
                <CardTitle className="text-sm">People catalog</CardTitle>
                <CardDescription className="text-xs">
                  Name, tag, and organize known people.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Not available yet
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </>
  )
}
