import { Component, type ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle } from "lucide-react"

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: string
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: "" }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo: errorInfo.componentStack || "" })
    try {
      const fs = (window as any).__TAURI__?.fs
      if (fs) {
        const msg = `REACT CRASH: ${error.message}\n${error.stack}\n${errorInfo.componentStack}`
        console.error(msg)
      }
    } catch {}
    console.error("React Error Boundary caught:", error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex items-center justify-center min-h-[60vh] p-6">
          <Card className="max-w-md border-red-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400">
                <AlertTriangle className="w-5 h-5" />
                Something went wrong
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                {this.state.error?.message || "An unexpected error occurred."}
              </p>
              {this.state.errorInfo && (
                <pre className="text-[10px] text-muted-foreground bg-muted p-2 rounded max-h-32 overflow-auto">
                  {this.state.errorInfo.slice(0, 500)}
                </pre>
              )}
              <Button size="sm" onClick={() => { this.setState({ hasError: false, error: null, errorInfo: "" }); window.location.href = "/" }}>
                Go to Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>
      )
    }
    return this.props.children
  }
}
