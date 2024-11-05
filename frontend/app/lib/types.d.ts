import { ClassValue } from "clsx";

declare module "@/lib/utils" {
  export function cn(...inputs: ClassValue[]): string;
}
