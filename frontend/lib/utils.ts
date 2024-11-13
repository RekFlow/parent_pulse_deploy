export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US").format(date);
}

export function logger(message: string, data?: any) {
  console.log(`[${new Date().toISOString()}] ${message}`, data || "");
}
