const cache = new Map<string, { data: any; timestamp: number }>()
const TTL = 60_000

export async function cachedCall<T>(key: string, fn: () => Promise<T>, ttl = TTL): Promise<T> {
  const cached = cache.get(key)
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data as T
  }
  const data = await fn()
  cache.set(key, { data, timestamp: Date.now() })
  return data
}

export function invalidateCache(prefix?: string) {
  if (prefix) {
    for (const key of cache.keys()) {
      if (key.startsWith(prefix)) cache.delete(key)
    }
  } else {
    cache.clear()
  }
}

const pending = new Map<string, Promise<any>>()

export async function dedupedCall<T>(key: string, fn: () => Promise<T>): Promise<T> {
  if (pending.has(key)) return pending.get(key) as Promise<T>
  const promise = fn().finally(() => pending.delete(key))
  pending.set(key, promise)
  return promise
}

const batchQueue: Array<{ path: string; resolve: Function }> = []
let batchTimer: any = null

export function batchEnrich(path: string): Promise<any> {
  return new Promise(resolve => {
    batchQueue.push({ path, resolve })
    if (!batchTimer) {
      batchTimer = setTimeout(async () => {
        const batch = batchQueue.splice(0)
        const paths = batch.map(b => b.path)
        const { enrichBatch } = await import("@/lib/tauri-bridge")
        const result = await enrichBatch(paths)
        batch.forEach((b, i) => b.resolve(result.files[i]))
        batchTimer = null
      }, 50)
    }
  })
}

export function prefetchEnrich(paths: string[]) {
  setTimeout(async () => {
    const { enrichBatch } = await import("@/lib/tauri-bridge")
    await enrichBatch(paths)
  }, 100)
}
