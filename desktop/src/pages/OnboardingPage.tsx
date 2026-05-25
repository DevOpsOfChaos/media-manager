import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useSettingsStore } from "@/stores/settings-store"
import { FolderOpen, Image, Check, ArrowRight, ChevronRight, ChevronLeft } from "lucide-react"
import { open } from "@tauri-apps/plugin-dialog"

const STEPS = [
  {
    title: "Welcome to Media Manager",
    description: "Organize, rename, and clean up your photo and video library — safely and with full undo support.",
    icon: Image,
    details: [
      "Preview every action before it happens",
      "Undo any operation from the history page",
      "Group associated files (RAW+JPEG, XMP sidecars)",
      "Find and remove exact duplicates",
    ],
  },
  {
    title: "Choose Your Media Sources",
    description: "Tell Media Manager where your photos and videos live. You can add more sources later in Settings or directly on each tool page.",
    icon: FolderOpen,
    details: [
      "You can scan multiple folders at once",
      "Subfolders are included automatically",
      "Your photos folder will be remembered as the default source",
    ],
  },
  {
    title: "You're All Set!",
    description: "Start exploring the tools. We recommend beginning with Organize to preview how your files would be sorted, or Duplicates to find wasted space.",
    icon: Check,
    details: [
      "Organize: sort files into year/month/day folders",
      "Duplicates: find and remove byte-identical copies",
      "History: review past runs and undo if needed",
      "Dashboard: your home base with quick workflows",
    ],
  },
]

export default function OnboardingPage() {
  const [step, setStep] = useState(0)
  const navigate = useNavigate()
  const { updateSettings, save } = useSettingsStore()
  const [selectedFolder, setSelectedFolder] = useState<string>(
    () => localStorage.getItem("default_source_dir") || ""
  )

  const browseFolder = async () => {
    try {
      const dir = await open({ directory: true, multiple: false, title: "Select your photos folder" })
      if (dir && typeof dir === "string") {
        setSelectedFolder(dir)
        localStorage.setItem("default_source_dir", dir)
      }
    } catch { /* dialog may not be available */ }
  }

  const currentStep = STEPS[step]
  const isLast = step === STEPS.length - 1

  const handleFinish = async () => {
    updateSettings({ show_onboarding: false })
    await save()
    navigate("/")
  }

  const handleSkip = async () => {
    updateSettings({ show_onboarding: false })
    await save()
    navigate("/")
  }

  return (
    <div className="flex items-center justify-center min-h-[80vh] p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto mb-4 flex items-center justify-center w-16 h-16 rounded-full bg-primary/10">
            {(() => {
              const Icon = currentStep.icon
              return <Icon className="w-8 h-8 text-primary" />
            })()}
          </div>
          <CardTitle className="text-xl">{currentStep.title}</CardTitle>
          <p className="text-sm text-muted-foreground mt-2">{currentStep.description}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Step indicators */}
          <div className="flex justify-center gap-2">
            {STEPS.map((_, i) => (
              <div
                key={i}
                className={`w-2.5 h-2.5 rounded-full transition-colors ${
                  i === step ? "bg-primary" : i < step ? "bg-primary/40" : "bg-muted"
                }`}
              />
            ))}
          </div>

          {step === 1 && (
            <div className="my-4 p-4 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-sm font-medium mb-2">Select your photos folder</p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={browseFolder}
                  className="flex-1"
                >
                  <FolderOpen className="w-4 h-4 mr-2" />
                  {selectedFolder 
                    ? selectedFolder.split(/[\\/]/).pop() || selectedFolder
                    : "Choose folder..."}
                </Button>
              </div>
              {selectedFolder && (
                <p className="text-xs text-muted-foreground mt-2 truncate">{selectedFolder}</p>
              )}
            </div>
          )}

          {/* Step details */}
          <ul className="space-y-2">
            {currentStep.details.map((detail, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Check className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                <span className="text-muted-foreground">{detail}</span>
              </li>
            ))}
          </ul>

          {/* Navigation */}
          <div className="flex items-center justify-between pt-2">
            <Button variant="ghost" size="sm" onClick={handleSkip}>
              Skip
            </Button>
            <div className="flex gap-2">
              {step > 0 && (
                <Button variant="outline" size="sm" onClick={() => setStep(step - 1)}>
                  <ChevronLeft className="w-4 h-4 mr-1" /> Back
                </Button>
              )}
              {isLast ? (
                <Button size="sm" onClick={handleFinish}>
                  Start Exploring <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              ) : (
                <Button size="sm" onClick={() => setStep(step + 1)}>
                  Next <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
