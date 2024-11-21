import * as React from "react";

export function Input({
  className,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`rounded-md border border-gray-300 px-4 py-2 ${className}`}
      {...props}
    />
  );
}

// Add logging for development/debugging
if (process.env.NODE_ENV === "development") {
  console.log("Input component loaded");
}
