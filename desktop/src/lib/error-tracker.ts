export function trackError(context: string, error: unknown) {
  console.error(`[${context}]`, error)
}
