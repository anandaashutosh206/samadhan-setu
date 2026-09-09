import type { Metadata } from "next";
import { Sora, Inter, JetBrains_Mono, Noto_Sans_Devanagari } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { NavBar } from "@/components/NavBar";

const sora = Sora({ subsets: ["latin"], weight: ["600", "700"], variable: "--font-sora" });
const inter = Inter({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-inter" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains" });
const notoDevanagari = Noto_Sans_Devanagari({ subsets: ["devanagari"], variable: "--font-noto-devanagari" });

export const metadata: Metadata = {
  title: "Samadhan Setu — Jharkhand Societal Innovation Portal",
  description: "Crowdsource societal challenges and route them to universities, industry, and government for collaborative solutions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${sora.variable} ${inter.variable} ${jetbrainsMono.variable} ${notoDevanagari.variable} font-inter antialiased`}>
        <Providers>
          <NavBar />
          <main className="mx-auto max-w-7xl px-4 pb-16 pt-6 sm:px-6 lg:px-8">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
