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
  if (msg.includes("DiskFull") || msg.includes("No space"))
    return "Not enough disk space. Free up space and try again."
  return msg.split("\n")[0].slice(0, 200)
}
