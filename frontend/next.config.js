/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    dangerouslyAllowSVG: true,
    contentDispositionType: "attachment",
    remotePatterns: [{ protocol: "https", hostname: "*" }],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://astrashield.onrender.com/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;