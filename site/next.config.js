/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  trailingSlash: false,
  async headers() {
    const link = [
      '</llms.txt>; rel="describedby"; type="text/markdown"',
      '</.well-known/api-catalog>; rel="api-catalog"',
      '</openapi.json>; rel="service-desc"; type="application/openapi+json"',
      '</sitemap.xml>; rel="sitemap"; type="application/xml"',
    ].join(', ')
    return [
      { source: '/', headers: [{ key: 'Link', value: link }] },
      { source: '/((?!api/|_next/).*)', headers: [{ key: 'Vary', value: 'Accept' }] },
    ]
  },
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'img.youtube.com',
        pathname: '/vi/**',
      },
      {
        protocol: 'https',
        hostname: 'i.ytimg.com',
        pathname: '/**',
      },
    ],
  },
}

module.exports = nextConfig
