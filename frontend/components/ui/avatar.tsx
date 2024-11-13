import * as React from "react";
import * as AvatarPrimitive from "@radix-ui/react-avatar";

export function Avatar({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <AvatarPrimitive.Root
      className={`relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full ${className}`}
    >
      {children}
    </AvatarPrimitive.Root>
  );
}

export function AvatarImage({
  src,
  alt,
  className,
}: {
  src: string;
  alt: string;
  className?: string;
}) {
  return (
    <AvatarPrimitive.Image
      src={src}
      alt={alt}
      className={`aspect-square h-full w-full ${className}`}
    />
  );
}

export function AvatarFallback({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <AvatarPrimitive.Fallback
      className={`flex h-full w-full items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 ${className}`}
    >
      {children}
    </AvatarPrimitive.Fallback>
  );
}
