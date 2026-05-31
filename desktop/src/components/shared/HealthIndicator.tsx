import { Activity } from "lucide-react"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

export function HealthIndicator({ score, issues }: { score: number; issues: number }) {
  return (
    <Tooltip>
      <TooltipTrigger>
        <div className={`flex items-center gap-1 text-xs ${score >= 90 ? 'text-green-500 dark:text-green-400' : score >= 70 ? 'text-amber-500 dark:text-amber-400' : 'text-red-500 dark:text-red-400'}`}>
          <Activity className="h-3 w-3" />
          {issues > 0 && <span>{issues}</span>}
        </div>
      </TooltipTrigger>
      <TooltipContent>
        <p>{score}% healthy</p>
        {issues > 0 && <p className="text-red-400">{issues} issues found</p>}
      </TooltipContent>
    </Tooltip>
  )
}
