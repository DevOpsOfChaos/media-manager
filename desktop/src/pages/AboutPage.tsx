import { useT } from "@/lib/i18n"
import { PageHeader } from "@/components/layout/PageHeader"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Code2, Coffee, Heart, Star, ExternalLink } from "lucide-react"


const GithubIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
  </svg>
)

export default function AboutPage() {
  const t = useT()

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <PageHeader
        title={t("Media Manager", "Media Manager")}
        subtitle={t("Local-first media workflow assistant — v0.6.0 Pre-Alpha", "Lokaler Medien-Workflow-Assistent — v0.6.0 Pre-Alpha")}
      />
      <Separator />

      {/* Developer section */}
      <Card>
        <CardHeader>
          <CardTitle>{t("Developer", "Entwickler")}</CardTitle>
          <CardDescription>
            {t("Created with care by a solo developer who loves clean code and organized photos.",
               "Mit Sorgfalt entwickelt von einem Solo-Entwickler, der sauberen Code und organisierte Fotos liebt.")}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <Code2 className="h-5 w-5" />
            <span className="font-medium">Manu</span>
            <a href="https://github.com/mries" target="_blank" rel="noopener noreferrer"
               className="text-primary hover:underline inline-flex items-center gap-1">
              <GithubIcon className="h-4 w-4" /> github.com/mries <ExternalLink className="h-3 w-3" />
            </a>
          </div>
          <p className="text-sm text-muted-foreground">
            {t("Built with Python, Rust, React, and Tauri — open source under MIT license.",
               "Entwickelt mit Python, Rust, React und Tauri — Open Source unter MIT-Lizenz.")}
          </p>
        </CardContent>
      </Card>

      {/* Support section */}
      <Card className="border-primary/20 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" fill="currentColor" />
            {t("Support the Project", "Unterstütze das Projekt")}
          </CardTitle>
          <CardDescription>
            {t("Media Manager is free and open source. If it saves you hours of organizing, consider supporting its development. Every bit helps keep the coffee flowing and the code improving!",
               "Media Manager ist kostenlos und Open Source. Wenn es dir Stunden beim Organisieren spart, unterstütze die Entwicklung. Jeder Beitrag hält den Kaffee am Fließen und den Code am Wachsen!")}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <a href="https://www.paypal.com/" target="_blank" rel="noopener noreferrer">
              <Button variant="default" size="lg" className="gap-2">
                <Coffee className="h-4 w-4" />
                {t("Support via PayPal", "Via PayPal unterstützen")}
              </Button>
            </a>
            <a href="https://www.patreon.com/" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" size="lg" className="gap-2">
                <Heart className="h-4 w-4" />
                {t("Support on Patreon", "Auf Patreon unterstützen")}
              </Button>
            </a>
          </div>
          <p className="text-xs text-muted-foreground">
            {t("Specific donation links coming soon. For now, these go to the platform homepages.",
               "Spezifische Spenden-Links folgen demnächst. Aktuell führen diese zu den Plattform-Startseiten.")}
          </p>
        </CardContent>
      </Card>

      {/* Star section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5 text-yellow-500" fill="currentColor" />
            {t("Star on GitHub", "GitHub-Star geben")}
          </CardTitle>
          <CardDescription>
            {t("If you find Media Manager useful, a GitHub star helps others discover it and motivates continued development!",
               "Wenn dir Media Manager gefällt, hilft ein GitHub-Star anderen, es zu entdecken und motiviert die Weiterentwicklung!")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <a href="https://github.com/mries/media-manager" target="_blank" rel="noopener noreferrer">
            <Button variant="secondary" size="lg" className="gap-2">
              <Star className="h-4 w-4" fill="currentColor" />
              {t("Star on GitHub", "Auf GitHub starren")}
            </Button>
          </a>
        </CardContent>
      </Card>


      {/* Tech stack */}
      <Card>
        <CardHeader>
          <CardTitle>{t("Tech Stack", "Technologie-Stack")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">Python</span> Core Engine</div>
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">Rust</span> Desktop Shell</div>
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">React 19</span> Frontend</div>
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">Tauri v2</span> App Framework</div>
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">TypeScript</span> Type Safety</div>
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">Tailwind</span> Styling</div>
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">dlib</span> Face Recognition</div>
            <div className="flex items-center gap-2"><span className="font-mono text-xs px-1.5 py-0.5 rounded bg-muted">ExifTool</span> Metadata</div>
          </div>
        </CardContent>
      </Card>

      {/* License */}
      <p className="text-center text-xs text-muted-foreground">
        MIT License · {new Date().getFullYear()} · Media Manager
      </p>
    </div>
  )
}
