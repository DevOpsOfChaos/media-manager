import { Loader2 } from "lucide-react"

interface ProgressBlockProps {
  phase: number
  totalPhases: number
  progress: number
  log: string[]
}

export function ProgressBlock({ phase, totalPhases, progress, log }: ProgressBlockProps) {
  return (
    <div className="space-y-3 p-4">
      <div className="flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">Processing...</span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full transition-all duration-700"
          style={{ width: `${Math.max(progress, 1)}%` }} />
      </div>
      <div className="flex gap-1">
        {Array.from({ length: totalPhases }).map((_, i) => (
          <div key={i} className={`flex-1 h-1 rounded-full ${phase > i ? 'bg-blue-500' : 'bg-muted'}`} />
        ))}
      </div>
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Phase {Math.min(phase, totalPhases)}/{totalPhases}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="max-h-24 overflow-y-auto bg-muted/20 rounded p-2 space-y-0.5">
        {log.map((msg, i) => (
          <p key={i} className="text-xs text-muted-foreground font-mono">{msg}</p>
        ))}
      </div>
    </div>
  )
}
