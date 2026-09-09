import { Card } from "@/components/ui/primitives";

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="font-sora text-2xl font-bold">About Samadhan Setu</h1>
      <Card>
        <p className="text-sm leading-relaxed">
          Samadhan Setu (SIH26043) is a digital platform built for the Government of Jharkhand&apos;s Department
          of Higher &amp; Technical Education to crowdsource societal challenges and route them through an
          AI-assisted pipeline to the universities, students, and industry partners best equipped to solve them.
        </p>
        <p className="mt-3 text-sm leading-relaxed">
          The platform runs its AI classification, deduplication, prioritisation, and university-matching entirely
          offline — no external API keys are required for core functionality.
        </p>
      </Card>
    </div>
  );
}
