interface Props { score: number; grade: string }
export function MetadataScoreBadge({ score, grade }: Props) {
  const color = grade === 'A' ? 'bg-green-500 dark:bg-green-600' : grade === 'B' ? 'bg-blue-500 dark:bg-blue-600' : grade === 'C' ? 'bg-amber-500 dark:bg-amber-600' : 'bg-red-500 dark:bg-red-600'
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-8 h-8 rounded-full ${color} flex items-center justify-center text-white text-xs font-bold`}>
        {grade}
      </div>
      <div>
        <p className="text-xs font-medium">{score}%</p>
        <p className="text-[9px] text-muted-foreground">Metadata score</p>
      </div>
    </div>
  )
}
