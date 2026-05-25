import { Star } from "lucide-react"

interface StarRatingProps {
  value: number
  onChange?: (value: number) => void
  readonly?: boolean
  size?: "sm" | "md"
}

export function StarRating({ value, onChange, readonly = false, size = "md" }: StarRatingProps) {
  const iconSize = size === "sm" ? "h-3 w-3" : "h-4 w-4"

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <button
          key={i}
          disabled={readonly}
          onClick={(e) => { e.stopPropagation(); onChange?.(i === value ? 0 : i) }}
          className={`${readonly ? "cursor-default" : "cursor-pointer hover:scale-110"} transition-transform`}
          aria-label={`${i} star${i !== 1 ? "s" : ""}`}
        >
          <Star
            className={`${iconSize} ${
              i <= value
                ? "text-yellow-500 fill-yellow-500"
                : "text-muted-foreground/30"
            }`}
          />
        </button>
      ))}
    </div>
  )
}
