import type { LucideIcon } from "lucide-react"
import { Inbox } from "lucide-react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import type { ReactNode } from "react"

const VARIANTS = {
  'no-files': { icon: '📁', titleEn: 'No files yet', titleDe: 'Noch keine Dateien', actionEn: 'Browse folder', actionDe: 'Ordner durchsuchen' },
  'no-people': { icon: '👤', titleEn: 'No people found', titleDe: 'Keine Personen gefunden', actionEn: 'Scan for faces', actionDe: 'Nach Gesichtern scannen' },
  'no-duplicates': { icon: '✨', titleEn: 'No duplicates!', titleDe: 'Keine Duplikate!', actionEn: 'Scan another folder', actionDe: 'Anderen Ordner scannen' },
  'no-runs': { icon: '📋', titleEn: 'No history yet', titleDe: 'Noch kein Verlauf', actionEn: 'Run organize or rename', actionDe: 'Organisieren oder umbenennen' },
  'no-results': { icon: '🔍', titleEn: 'No results found', titleDe: 'Keine Ergebnisse', actionEn: 'Try different filters', actionDe: 'Andere Filter versuchen' },
  'error': { icon: '⚠️', titleEn: 'Something went wrong', titleDe: 'Etwas ist schiefgelaufen', actionEn: 'Try again', actionDe: 'Erneut versuchen' },
  'welcome': { icon: '👋', titleEn: 'Welcome!', titleDe: 'Willkommen!', actionEn: 'Get started', actionDe: 'Loslegen' },
} as const

interface EmptyStateProps {
  variant?: keyof typeof VARIANTS
  icon?: string | LucideIcon
  title?: string
  description?: string
  action?: ReactNode
  onAction?: () => void
}

export function EmptyState({ variant, icon: iconProp, title: titleProp, description, action: actionProp, onAction }: EmptyStateProps) {
  const t = useT()

  const v = variant ? VARIANTS[variant] : null
  const icon = iconProp ?? v?.icon ?? Inbox
  const title = titleProp ?? (v ? t(v.titleEn, v.titleDe) : "")
  const action = actionProp ?? (v && onAction ? <Button onClick={onAction}>{t(v.actionEn, v.actionDe)}</Button> : null)

  const isEmoji = typeof icon === "string"
  const IconComp = isEmoji ? Inbox : (icon as LucideIcon)

  return (
    <div className="flex flex-col items-center justify-center py-16 text-center rounded-lg bg-gradient-to-b from-muted/30 to-muted/10">
      <div className="rounded-full bg-gradient-to-br from-primary/10 to-primary/5 p-5 mb-4 animate-pulse">
        {isEmoji ? (
          <span className="text-3xl leading-none">{icon as string}</span>
        ) : (
          <IconComp className="size-10 text-primary/50" strokeWidth={1.5} />
        )}
      </div>
      <p className="text-base font-semibold">{title}</p>
      {description && (
        <p className="text-sm text-muted-foreground mt-2 max-w-sm">
          {description}
        </p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}
