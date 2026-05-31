export interface FriendlyError {
  message: string
  suggestion: string | null
}

const PATTERNS: Array<{ match: RegExp; message: string; suggestion: string }> = [
  { match: /source.*required/i, message: "Source directory is required", suggestion: "Click 'Browse' to select a folder with your photos." },
  { match: /target.*required/i, message: "Target directory is required", suggestion: "Choose where organized files should go." },
  { match: /not found/i, message: "File or folder not found", suggestion: "The path may have been moved or deleted. Check the location." },
  { match: /permission denied/i, message: "Permission denied", suggestion: "Run the app as administrator or choose a different folder." },
  { match: /disk.*full/i, message: "Not enough disk space", suggestion: "Free up space or choose a different target drive." },
  { match: /too many|limit/i, message: "Too many files selected", suggestion: "Try with a smaller folder or fewer files." },
]

export function userFriendlyError(err: unknown): FriendlyError {
  if (!err) return { message: "An unexpected error occurred", suggestion: null }
  const msg = String(err)

  const pattern = PATTERNS.find(p => p.match.test(msg))
  if (pattern) return { message: pattern.message, suggestion: pattern.suggestion }

  if (msg.includes("FileNotFoundError") || msg.includes("No such file"))
    return { message: "File not found. Check that the directory still exists.", suggestion: null }
  if (msg.includes("PermissionError") || msg.includes("Permission denied"))
    return { message: "Permission denied. Try running as administrator or choosing a different directory.", suggestion: null }
  if (msg.includes("JSONDecodeError") || msg.includes("json"))
    return { message: "Data format error. The configuration may be corrupted.", suggestion: null }
  if (msg.includes("ConnectionRefused") || msg.includes("Connection reset"))
    return { message: "Could not connect to the media processing engine. Try restarting the app.", suggestion: null }
  if (msg.includes("timeout") || msg.includes("Timeout"))
    return { message: "The operation timed out. Try with a smaller directory or fewer files.", suggestion: null }
  if (msg.includes("DiskFull") || msg.includes("No space") || msg.includes("ENOSPC"))
    return { message: "Not enough disk space. Free up space and try again.", suggestion: null }
  if (msg.includes("MemoryError") || msg.includes("OutOfMemory") || msg.includes("out of memory"))
    return { message: "Out of memory. Try processing fewer files at once or closing other applications.", suggestion: null }
  if (msg.includes("FileNotFound") || msg.includes("ENOENT") || msg.includes("does not exist"))
    return { message: "File or directory not found. Verify the path is correct.", suggestion: null }
  if (msg.includes("PermissionError") || msg.includes("EACCES") || msg.includes("Not permitted"))
    return { message: "Permission denied. Try running with elevated privileges.", suggestion: null }
  if (msg.includes("OSError") || msg.includes("IOError") || msg.includes("File exists") || msg.includes("EEXIST"))
    return { message: "A file system error occurred. Check available disk space and permissions.", suggestion: null }
  if (msg.includes("ConnectionError") || msg.includes("NetworkError") || msg.includes("ECONNREFUSED"))
    return { message: "Network error. Check your internet connection and try again.", suggestion: null }
  if (msg.includes("ImportError") || msg.includes("ModuleNotFoundError"))
    return { message: "A required component is missing. Try reinstalling the application.", suggestion: null }
  if (msg.includes("not enough memory") || msg.includes("Cannot allocate memory"))
    return { message: "System is running low on memory. Close other applications and try again.", suggestion: null }
  if (msg.includes("read-only") || msg.includes("Read-only") || msg.includes("EROFS"))
    return { message: "Cannot write to a read-only location. Choose a writable directory.", suggestion: null }
  if (msg.includes("Too many open files") || msg.includes("EMFILE"))
    return { message: "Too many files open. The application hit a system limit. Restart the app.", suggestion: null }
  return { message: msg.split("\n")[0].slice(0, 200), suggestion: null }
}
