interface ErrorBannerProps {
  message: string
  suggestion?: string | null
  details?: string[]
}

export function ErrorBanner({ message, suggestion, details }: ErrorBannerProps) {
  return (
    <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive space-y-1">
      <p className="font-medium">{message}</p>
      {suggestion && <p className="text-xs text-muted-foreground">{suggestion}</p>}
      {details?.map((d, i) => (
        <p key={i} className="text-xs font-mono truncate">
          {d}
        </p>
      ))}
    </div>
  )
}
