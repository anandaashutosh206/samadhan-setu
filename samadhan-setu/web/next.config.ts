import type { NextConfig } from "next";

const apiHost = (() => {
  try {
    return new URL(process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").hostname;
  } catch {
    return "localhost";
  }
})();

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/uploads/**" },
      { protocol: "https", hostname: apiHost, pathname: "/uploads/**" },
    ],
  },
};

export default nextConfig;
