import { Inbox } from "lucide-react"

interface EmptyStateProps {
  title: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center rounded-lg bg-gradient-to-b from-muted/30 to-muted/10">
      <div className="rounded-full bg-gradient-to-br from-primary/10 to-primary/5 p-5 mb-4 animate-pulse">
        <Inbox className="size-10 text-primary/50" strokeWidth={1.5} />
      </div>
      <p className="text-base font-semibold">{title}</p>
      {description && (
        <p className="text-sm text-muted-foreground mt-2 max-w-sm">
          {description}
        </p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}
