import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function DashboardPage() {
  return (
    <>
      <PageHeader title="Dashboard" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Welcome</CardTitle>
              <CardDescription>
                Media Manager helps you organize, deduplicate, and manage your
                media files.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Dashboard content will be implemented in the next phase.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}
