interface TagCloudProps {
  tags: string[]
  onTagClick?: (tag: string) => void
  max?: number
  selectedTags?: string[]
  onToggle?: (tag: string) => void
}

export function TagCloud({ tags, onTagClick, max = 20, selectedTags, onToggle }: TagCloudProps) {
  if (tags.length === 0) return null

  if (selectedTags !== undefined && onToggle) {
    return (
      <div className="flex flex-wrap gap-1">
        {tags.map(tag => (
          <button
            key={tag}
            onClick={() => onToggle(tag)}
            className={`text-[11px] px-2 py-0.5 rounded-full border transition-colors ${
              selectedTags.includes(tag)
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-background text-muted-foreground border-border hover:border-primary/50"
            }`}
          >
            {tag}
          </button>
        ))}
      </div>
    )
  }

  const displayed = tags.slice(0, max)
  return (
    <div className="flex flex-wrap gap-1">
      {displayed.map(tag => {
        const [category, ...value] = tag.split(':')
        const label = value.join(':') || category
        return (
          <button key={tag} onClick={() => onTagClick?.(tag)}
            className="text-[10px] px-1.5 py-0.5 rounded-full bg-muted hover:bg-primary/10 border transition-colors">
            <span className="text-muted-foreground">{category}:</span>
            {label}
          </button>
        )
      })}
    </div>
  )
}
