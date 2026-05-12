interface StatusBadgeProps {
  ok: boolean
  label: string
  detail?: string
}

export function StatusBadge({ ok, label, detail }: StatusBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex size-2 shrink-0 rounded-full ${
          ok ? "bg-green-500" : "bg-destructive"
        }`}
      />
      <span className="text-sm font-medium">{label}</span>
      {detail && (
        <span className="truncate text-xs text-muted-foreground">
          {detail}
        </span>
      )}
    </div>
  )
}
