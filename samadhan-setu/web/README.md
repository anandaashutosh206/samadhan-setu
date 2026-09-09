# Samadhan Setu — Web

Next.js 15 (App Router) + React 19 + TypeScript frontend. See the top-level `README.md` for the full setup walkthrough.

Quick reference:
- `npm install --legacy-peer-deps` (required — see root README troubleshooting for why)
- `npm run dev` — starts on `http://localhost:3000`
- `npm run type-check` / `npm run lint` / `npm run build`
- API base URL comes from `NEXT_PUBLIC_API_URL` in `.env.local` (copy from `.env.example`)
- UI primitives live in `src/components/ui/`; showcase components (`ChallengeCard`, `AITriagePanel`, `ProjectLifecycle`) live in `src/components/`
