import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function OrganizePage() {
  return (
    <>
      <PageHeader title="Organize" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Organize Media Files</CardTitle>
              <CardDescription>
                Scan your sources, preview the plan, and apply the organization.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Organize workflow will be implemented in the next phase.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}
