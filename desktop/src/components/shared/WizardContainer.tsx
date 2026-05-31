import { useState, useCallback } from "react"
import { useT } from "@/lib/i18n"
import { StepIndicator } from "@/components/shared/StepIndicator"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import type { ReactNode } from "react"

interface WizardStep {
  id: string
  label: string
  labelDe: string
}

interface WizardContainerProps {
  steps: WizardStep[]
  children: (props: {
    step: number
    data: Record<string, any>
    setData: (key: string, value: any) => void
    goNext: () => void
    goBack: () => void
    goTo: (step: number) => void
    isFirst: boolean
    isLast: boolean
    footer: ReactNode
  }) => ReactNode
  onFinish?: () => void
  initialData?: Record<string, any>
}

export function WizardContainer({ steps, children, onFinish, initialData = {} }: WizardContainerProps) {
  const t = useT()
  const [step, setStep] = useState(0)
  const [data, setDataState] = useState(initialData)

  const setData = useCallback((key: string, value: any) => {
    setDataState(prev => ({ ...prev, [key]: value }))
  }, [])

  const goNext = () => {
    if (step < steps.length - 1) setStep(s => s + 1)
    else onFinish?.()
  }
  const goBack = () => { if (step > 0) setStep(s => s - 1) }
  const goTo = (s: number) => { if (s >= 0 && s < steps.length) setStep(s) }

  const isFirst = step === 0
  const isLast = step === steps.length - 1

  const stepDefs = steps.map((s, i) => ({
    id: s.id,
    label: t(s.label, s.labelDe),
    done: i < step,
    active: i === step,
  }))

  const footer = (
    <div className="flex items-center justify-between mt-8 pt-4 border-t">
      <div>
        {!isFirst && (
          <Button variant="outline" size="sm" onClick={goBack}>
            <ChevronLeft className="h-4 w-4 mr-1" /> {t("Back", "Zurück")}
          </Button>
        )}
      </div>
      <div className="text-xs text-muted-foreground">
        {step + 1} / {steps.length}
      </div>
      <div>
      </div>
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto p-6">
      <StepIndicator steps={stepDefs} />
      {children({ step, data, setData, goNext, goBack, goTo, isFirst, isLast, footer })}
    </div>
  )
}
