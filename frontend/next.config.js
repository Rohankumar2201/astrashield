/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow images from any domain (for the base64 ELA images from the backend)
  images: {
    dangerouslyAllowSVG: true,
    contentDispositionType: "attachment",
    remotePatterns: [{ protocol: "http", hostname: "localhost" }],
  },
};

module.exports = nextConfig;
