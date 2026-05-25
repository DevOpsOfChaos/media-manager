interface TagCloudProps {
  tags: string[]
  selectedTags: string[]
  onToggle: (tag: string) => void
}

export function TagCloud({ tags, selectedTags, onToggle }: TagCloudProps) {
  if (tags.length === 0) return null

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
