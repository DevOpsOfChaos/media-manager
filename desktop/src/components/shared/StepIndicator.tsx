interface Step { id: string; label: string; done?: boolean; active?: boolean }

export function StepIndicator({ steps }: { steps: Step[] }) {
  return (
    <div className="flex items-center gap-2 mb-6">
      {steps.map((step, i) => (
        <div key={step.id} className="flex items-center gap-2">
          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
            step.done ? 'bg-green-500 text-white' : 
            step.active ? 'bg-primary text-primary-foreground ring-2 ring-primary/30' : 
            'bg-muted text-muted-foreground'
          }`}>
            {step.done ? '\u2713' : i + 1}
          </div>
          <span className={`text-xs ${step.active ? 'font-medium' : 'text-muted-foreground'}`}>
            {step.label}
          </span>
          {i < steps.length - 1 && (
            <div className={`w-8 h-0.5 ${step.done ? 'bg-green-500' : 'bg-muted'}`} />
          )}
        </div>
      ))}
    </div>
  )
}
