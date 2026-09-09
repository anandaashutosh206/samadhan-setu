import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <p className="font-sora text-4xl font-bold text-primary">404</p>
      <p className="text-muted">This page doesn&apos;t exist.</p>
      <Link href="/" className="text-sm text-primary underline">Back to home</Link>
    </div>
  );
}
