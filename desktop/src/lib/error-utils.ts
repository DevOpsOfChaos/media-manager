export function userFriendlyError(err: unknown): string {
  if (!err) return "An unexpected error occurred"
  const msg = String(err)
  if (msg.includes("FileNotFoundError") || msg.includes("No such file"))
    return "File not found. Check that the directory still exists."
  if (msg.includes("PermissionError") || msg.includes("Permission denied"))
    return "Permission denied. Try running as administrator or choosing a different directory."
  if (msg.includes("JSONDecodeError") || msg.includes("json"))
    return "Data format error. The configuration may be corrupted."
  if (msg.includes("ConnectionRefused") || msg.includes("Connection reset"))
    return "Could not connect to the media processing engine. Try restarting the app."
  if (msg.includes("timeout") || msg.includes("Timeout"))
    return "The operation timed out. Try with a smaller directory or fewer files."
  if (msg.includes("DiskFull") || msg.includes("No space") || msg.includes("ENOSPC"))
    return "Not enough disk space. Free up space and try again."
  if (msg.includes("MemoryError") || msg.includes("OutOfMemory") || msg.includes("out of memory"))
    return "Out of memory. Try processing fewer files at once or closing other applications."
  if (msg.includes("FileNotFound") || msg.includes("ENOENT") || msg.includes("does not exist"))
    return "File or directory not found. Verify the path is correct."
  if (msg.includes("PermissionError") || msg.includes("EACCES") || msg.includes("Not permitted"))
    return "Permission denied. Try running with elevated privileges."
  if (msg.includes("OSError") || msg.includes("IOError") || msg.includes("File exists") || msg.includes("EEXIST"))
    return "A file system error occurred. Check available disk space and permissions."
  if (msg.includes("ConnectionError") || msg.includes("NetworkError") || msg.includes("ECONNREFUSED"))
    return "Network error. Check your internet connection and try again."
  if (msg.includes("ImportError") || msg.includes("ModuleNotFoundError"))
    return "A required component is missing. Try reinstalling the application."
  if (msg.includes("not enough memory") || msg.includes("Cannot allocate memory"))
    return "System is running low on memory. Close other applications and try again."
  if (msg.includes("read-only") || msg.includes("Read-only") || msg.includes("EROFS"))
    return "Cannot write to a read-only location. Choose a writable directory."
  if (msg.includes("Too many open files") || msg.includes("EMFILE"))
    return "Too many files open. The application hit a system limit. Restart the app."
  return msg.split("\n")[0].slice(0, 200)
}
