"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <p className="font-sora text-2xl font-bold text-danger">Something went wrong</p>
      <p className="max-w-md text-sm text-muted">
        An unexpected error occurred while loading this page. You can try again, or head back to the homepage.
      </p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
