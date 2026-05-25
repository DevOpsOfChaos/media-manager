import { useState, useRef, KeyboardEvent } from "react"
import { useT } from "@/lib/i18n"
import { X } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface TagInputProps {
  tags: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
}

export function TagInput({ tags, onChange, placeholder }: TagInputProps) {
  const t = useT()
  const [input, setInput] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  const addTag = (tag: string) => {
    const trimmed = tag.trim().toLowerCase()
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed])
    }
    setInput("")
  }

  const removeTag = (tag: string) => {
    onChange(tags.filter(t => t !== tag))
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault()
      addTag(input)
    } else if (e.key === "Backspace" && !input && tags.length > 0) {
      removeTag(tags[tags.length - 1])
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-1 p-1.5 border rounded-md min-h-[36px] bg-background focus-within:ring-1 focus-within:ring-ring cursor-text"
      onClick={() => inputRef.current?.focus()}>
      {tags.map(tag => (
        <Badge key={tag} variant="secondary" className="gap-1 text-[10px] py-0">
          {tag}
          <button onClick={(e) => { e.stopPropagation(); removeTag(tag) }}
            className="hover:text-red-500 transition-colors">
            <X className="h-2.5 w-2.5" />
          </button>
        </Badge>
      ))}
      <input
        ref={inputRef}
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={tags.length === 0 ? (placeholder || t("Add tags...", "Tags hinzufügen...")) : ""}
        className="flex-1 min-w-[80px] bg-transparent border-none outline-none text-xs py-0.5"
      />
    </div>
  )
}
