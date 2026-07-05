/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Ensure proper module resolution
  transpilePackages: [],
  // Disable webpack cache for better reliability
  webpack: (config) => {
    config.cache = false;
    return config;
  },
}

module.exports = nextConfig
