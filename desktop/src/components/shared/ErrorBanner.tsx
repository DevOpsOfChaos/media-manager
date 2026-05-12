interface ErrorBannerProps {
  message: string
  details?: string[]
}

export function ErrorBanner({ message, details }: ErrorBannerProps) {
  return (
    <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive space-y-1">
      <p className="font-medium">{message}</p>
      {details?.map((d, i) => (
        <p key={i} className="text-xs font-mono truncate">
          {d}
        </p>
      ))}
    </div>
  )
}
