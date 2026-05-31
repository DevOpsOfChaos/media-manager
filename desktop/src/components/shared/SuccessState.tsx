import type { ReactNode } from "react"
import { Check } from "lucide-react"

function SuccessState({ message, action }: { message: string; action?: ReactNode }) {
  return (
    <div className="text-center py-12 space-y-4">
      <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mx-auto animate-bounce">
        <Check className="h-8 w-8 text-green-600" />
      </div>
      <h3 className="text-lg font-medium text-green-700 dark:text-green-400">{message}</h3>
      {action}
    </div>
  )
}

export { SuccessState }
