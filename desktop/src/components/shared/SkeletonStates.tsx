import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

function FileGridSkeleton({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
      {Array.from({ length: Math.min(Math.max(count, 8), 24) }).map((_, i) => (
        <div key={i} className="rounded-xl border bg-card overflow-hidden">
          <Skeleton className="aspect-[4/3] w-full rounded-none" />
          <div className="p-2.5 space-y-1.5">
            <Skeleton className="h-3 w-3/4" />
            <Skeleton className="h-2.5 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}

function DetailPanelSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="space-y-4 p-4">
      <Skeleton className="aspect-video w-full rounded-lg" />
      <Skeleton className="h-5 w-2/3" />
      <div className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <Skeleton className="h-3 w-16 shrink-0" />
            <Skeleton className={cn("h-3", i === 0 ? "w-3/4" : i === 1 ? "w-1/2" : i % 2 === 0 ? "w-2/3" : "w-1/3")} />
          </div>
        ))}
      </div>
      <Skeleton className="h-8 w-full rounded-lg" />
    </div>
  )
}

function StatsCardSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border bg-card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="size-6 rounded" />
          </div>
          <Skeleton className="h-7 w-16" />
          <Skeleton className="h-2.5 w-24" />
        </div>
      ))}
    </div>
  )
}

function ListSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-1">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 px-3 py-2.5 rounded-lg border border-transparent">
          <Skeleton className="size-8 rounded shrink-0" />
          <div className="flex-1 space-y-1 min-w-0">
            <Skeleton className="h-3.5 w-2/5" />
            <Skeleton className="h-2.5 w-1/3" />
          </div>
          <Skeleton className="h-4 w-12 shrink-0" />
        </div>
      ))}
    </div>
  )
}

export { FileGridSkeleton, DetailPanelSkeleton, StatsCardSkeleton, ListSkeleton }
