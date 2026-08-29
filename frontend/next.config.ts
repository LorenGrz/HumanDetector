import type { NextConfig } from "next";

// Export estático para GitHub Pages. `basePath` sólo en el build de Pages
// (se pasa NEXT_PUBLIC_BASE_PATH=/HumanDetector en el workflow); en local
// queda vacío y la app sirve en `/`. Se inlinea en build, no cambia en runtime.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: "export",
  basePath: basePath || undefined,
  images: { unoptimized: true },
};

export default nextConfig;
