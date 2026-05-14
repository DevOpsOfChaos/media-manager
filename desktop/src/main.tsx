import React, { Suspense, lazy } from "react"
import ReactDOM from "react-dom/client"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import App from "./App"
import "./index.css"

const DashboardPage = lazy(() => import("./pages/DashboardPage"))
const LibraryPage = lazy(() => import("./pages/LibraryPage"))
const OrganizePage = lazy(() => import("./pages/OrganizePage"))
const DuplicatesPage = lazy(() => import("./pages/DuplicatesPage"))
const PeoplePage = lazy(() => import("./pages/PeoplePage"))
const HistoryPage = lazy(() => import("./pages/HistoryPage"))
const RunDetailPage = lazy(() => import("./pages/RunDetailPage"))
const ReviewWorkbenchPage = lazy(() => import("./pages/ReviewWorkbenchPage"))
const SettingsPage = lazy(() => import("./pages/SettingsPage"))

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<App />}>
          <Route
            index
            element={
              <Suspense fallback={<PageFallback />}>
                <DashboardPage />
              </Suspense>
            }
          />
          <Route
            path="library"
            element={
              <Suspense fallback={<PageFallback />}>
                <LibraryPage />
              </Suspense>
            }
          />
          <Route
            path="organize"
            element={
              <Suspense fallback={<PageFallback />}>
                <OrganizePage />
              </Suspense>
            }
          />
          <Route
            path="duplicates"
            element={
              <Suspense fallback={<PageFallback />}>
                <DuplicatesPage />
              </Suspense>
            }
          />
          <Route
            path="people"
            element={
              <Suspense fallback={<PageFallback />}>
                <PeoplePage />
              </Suspense>
            }
          />
          <Route
            path="history"
            element={
              <Suspense fallback={<PageFallback />}>
                <HistoryPage />
              </Suspense>
            }
          />
          <Route
            path="history/:runId"
            element={
              <Suspense fallback={<PageFallback />}>
                <RunDetailPage />
              </Suspense>
            }
          />
          <Route
            path="review"
            element={
              <Suspense fallback={<PageFallback />}>
                <ReviewWorkbenchPage />
              </Suspense>
            }
          />
          <Route
            path="settings"
            element={
              <Suspense fallback={<PageFallback />}>
                <SettingsPage />
              </Suspense>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)

function PageFallback() {
  return (
    <main className="flex flex-1 items-center justify-center p-4">
      <p className="text-sm text-muted-foreground">Loading...</p>
    </main>
  )
}
