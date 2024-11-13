import * as React from "react";

export function Button({
  children,
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`rounded-md bg-primary px-4 py-2 text-white ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
