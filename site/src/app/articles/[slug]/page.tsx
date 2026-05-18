import { getPostData, getAllPostSlugs, getRelatedPosts, VideoInsights, FAQ, HowToStep } from '@/lib/posts'
import { notFound } from 'next/navigation'

export const revalidate = 3600 // Revalidate every hour
import {
  HeroImage,
  AnimatedBreadcrumb,
  AnimatedHeader,
  AnimatedArticleBody,
  AnimatedTags,
  AnimatedRelatedArticles,
  AnimatedCTA,
  AnimatedYouTubeSection,
  ScrollRevealYouTube,
  KeyStatCallout,
  FAQSection,
  TLDRSummary,
  LastUpdated,
  TableOfContents,
  PrintableChecklist
} from '@/components/ArticleContent'
import ShareButtons from '@/components/ShareButtons'
import ReadingProgress from '@/components/ReadingProgress'

// YouTube Video Embed Component with optional collapsible insights
function YouTubeEmbed({
  videoId,
  title,
  channel,
  insights
}: {
  videoId: string
  title: string
  channel: string
  insights?: VideoInsights
}) {
  const hasInsights = insights && (insights.key_points?.length || insights.best_quote || insights.pro_tips?.length)

  return (
    <div className="my-8">
      <div className="aspect-video rounded-xl overflow-hidden shadow-lg">
        <iframe
          src={`https://www.youtube.com/embed/${videoId}?rel=0`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="w-full h-full"
        />
      </div>
      <p className="text-sm text-gray-500 mt-2 text-center">
        📺 {title} • {channel}
      </p>

      {/* Collapsible Video Insights */}
      {hasInsights && (
        <details className="mt-4 bg-leaf-50 rounded-lg border border-leaf-200">
          <summary className="px-4 py-3 cursor-pointer text-leaf-800 font-medium hover:bg-leaf-100 rounded-lg transition-colors">
            📝 Video Highlights & Key Takeaways
          </summary>
          <div className="px-4 pb-4 pt-2 space-y-4">
            {/* Quote */}
            {insights.best_quote && (
              <blockquote className="border-l-4 border-leaf-400 pl-4 italic text-gray-700">
                "{insights.best_quote}"
                <footer className="text-sm text-leaf-600 mt-1 not-italic">— {channel}</footer>
              </blockquote>
            )}

            {/* Key Points */}
            {insights.key_points && insights.key_points.length > 0 && (
              <div>
                <h4 className="font-semibold text-leaf-800 mb-2">Key Points:</h4>
                <ul className="space-y-1">
                  {insights.key_points.slice(0, 4).map((point, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-gray-700">
                      <span className="text-leaf-500 mt-1">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Pro Tips */}
            {insights.pro_tips && insights.pro_tips.length > 0 && (
              <div>
                <h4 className="font-semibold text-leaf-800 mb-2">Pro Tips:</h4>
                <ul className="space-y-1">
                  {insights.pro_tips.slice(0, 3).map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-gray-700">
                      <span className="text-amber-500 mt-1">💡</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  )
}

export async function generateStaticParams() {
  const paths = getAllPostSlugs()
  return paths.map((path) => ({
    slug: path.params.slug,
  }))
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  try {
    const post = await getPostData(slug)
    const baseUrl = 'https://thegreenleaf.com'
    const imageUrl = post.featured_image
      ? `${baseUrl}${post.featured_image}`
      : `${baseUrl}/images/default-leaf-hero.jpg`

    return {
      title: `${post.title} - The Green Leaf`,
      description: post.meta_description,
      keywords: post.tags?.join(', '),
      authors: [{ name: 'The Green Leaf' }],
      openGraph: {
        title: post.title,
        description: post.meta_description,
        url: `${baseUrl}/articles/${slug}`,
        siteName: 'The Green Leaf',
        images: [
          {
            url: imageUrl,
            width: 1792,
            height: 1024,
            alt: post.featured_image_alt || post.title,
          },
        ],
        locale: 'en_US',
        type: 'article',
        publishedTime: post.generated_at,
        authors: ['The Green Leaf'],
        tags: post.tags,
      },
      twitter: {
        card: 'summary_large_image',
        title: post.title,
        description: post.meta_description,
        images: [imageUrl],
      },
      alternates: {
        canonical: `${baseUrl}/articles/${slug}`,
      },
    }
  } catch {
    return {
      title: 'Article Not Found - The Green Leaf',
    }
  }
}

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  let post

  try {
    post = await getPostData(slug)
  } catch {
    notFound()
  }

  // Get related articles
  const relatedPosts = getRelatedPosts(slug, 3)

  // Enhanced JSON-LD structured data for AI crawlers
  const baseUrl = 'https://thegreenleaf.com'
  const articleUrl = `${baseUrl}/articles/${slug}`
  const imageUrl = post.featured_image ? `${baseUrl}${post.featured_image}` : `${baseUrl}/images/default-leaf-hero.jpg`

  // Main Article Schema
  const articleSchema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    '@id': articleUrl,
    headline: post.title,
    alternativeHeadline: post.meta_description,
    description: post.meta_description,
    image: {
      '@type': 'ImageObject',
      url: imageUrl,
      width: 1792,
      height: 1024,
      caption: post.featured_image_alt || post.title,
    },
    datePublished: post.generated_at,
    dateModified: post.last_updated || post.generated_at,
    author: {
      '@type': 'Organization',
      name: 'The Green Leaf',
      url: baseUrl,
      logo: {
        '@type': 'ImageObject',
        url: `${baseUrl}/images/logo_accent.png`,
      },
    },
    publisher: {
      '@type': 'Organization',
      name: 'The Green Leaf',
      url: baseUrl,
      logo: {
        '@type': 'ImageObject',
        url: `${baseUrl}/images/logo_accent.png`,
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': articleUrl,
    },
    keywords: post.tags?.join(', '),
    articleSection: post.category || 'Cannabis',
    about: {
      '@type': 'Thing',
      name: post.keyword || 'cannabis',
    },
    inLanguage: 'en-US',
    isAccessibleForFree: true,
    isPartOf: {
      '@type': 'WebSite',
      '@id': `${baseUrl}/#website`,
      url: baseUrl,
      name: 'The Green Leaf',
    },
    wordCount: post.word_count,
    timeRequired: post.estimated_read_time,
    ...(post.sources && post.sources.length > 0 ? {
      citation: post.sources.map(source => ({
        '@type': 'CreativeWork',
        name: source.name,
        url: source.url,
      })),
    } : {}),
  }

  // Breadcrumb Schema for navigation context (with category level)
  const breadcrumbItems = [
    { '@type': 'ListItem', position: 1, name: 'Home', item: baseUrl },
    { '@type': 'ListItem', position: 2, name: 'Articles', item: `${baseUrl}/articles` },
  ]
  if (post.category) {
    breadcrumbItems.push({ '@type': 'ListItem', position: 3, name: post.category, item: `${baseUrl}/topics` })
    breadcrumbItems.push({ '@type': 'ListItem', position: 4, name: post.title, item: articleUrl })
  } else {
    breadcrumbItems.push({ '@type': 'ListItem', position: 3, name: post.title, item: articleUrl })
  }
  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbItems,
  }

  // FAQ Schema for AI citation (if FAQs exist)
  const faqSchema = post.faqs && post.faqs.length > 0 ? {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: post.faqs.map((faq: FAQ) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  } : null

  // VideoObject Schema for YouTube embeds
  const videoSchemas = post.youtube?.map(video => ({
    '@context': 'https://schema.org',
    '@type': 'VideoObject',
    name: video.title,
    description: `${video.title} by ${video.channel}`,
    thumbnailUrl: `https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`,
    uploadDate: post.generated_at,
    embedUrl: `https://www.youtube.com/embed/${video.id}`,
    contentUrl: `https://www.youtube.com/watch?v=${video.id}`,
    publisher: {
      '@type': 'Organization',
      name: video.channel,
    },
  })) || []

  // HowTo Schema for step-by-step articles (rich results)
  const howToSchema = post.howTo ? {
    '@context': 'https://schema.org',
    '@type': 'HowTo',
    name: post.howTo.name,
    description: post.meta_description,
    image: imageUrl,
    step: post.howTo.steps.map((step: HowToStep, index: number) => ({
      '@type': 'HowToStep',
      position: index + 1,
      name: step.name,
      text: step.text,
    })),
  } : null

  // Speakable Schema - points AI voice assistants to key content
  const speakableSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    '@id': `${articleUrl}#speakable`,
    speakable: {
      '@type': 'SpeakableSpecification',
      cssSelector: ['.quick-answer', '[itemprop="description"]', '[itemprop="headline"]'],
    },
  }

  // Combine schemas for comprehensive structured data
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const schemaGraph: any[] = [articleSchema, breadcrumbSchema, speakableSchema, ...videoSchemas]
  if (faqSchema) {
    schemaGraph.push(faqSchema)
  }
  if (howToSchema) {
    schemaGraph.push(howToSchema)
  }

  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': schemaGraph,
  }

  const heroVideo = post.youtube?.find(v => v.position === 'hero')
  const sectionVideo = post.youtube?.find(v => v.position === 'section' && v.insights)

  return (
    <>
      <ReadingProgress />
      {/* JSON-LD Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Semantic HTML5 article structure - optimized for AI crawlers */}
      <article
        className="min-h-screen bg-white"
        itemScope
        itemType="https://schema.org/Article"
      >
        {/* Hero Image Banner - Animated */}
        {post.featured_image && (
          <div className="print:hidden">
            <HeroImage
              src={post.featured_image}
              alt={post.featured_image_alt || post.title}
            />
          </div>
        )}

        <div className="max-w-4xl mx-auto px-4 py-12 print:py-4">
          <div className="print:hidden">
            {/* Breadcrumb Navigation - Animated */}
            <AnimatedBreadcrumb title={post.title} category={post.category} />

            {/* Article Header - Animated */}
            <AnimatedHeader
              season={post.season}
              category={post.category}
              readTime={post.estimated_read_time}
              wordCount={post.word_count}
              title={post.title}
              description={post.meta_description}
              generatedAt={post.generated_at}
              slug={slug}
            />

            {/* Hero YouTube Video (if present) - Animated on load */}
            {heroVideo && (
              <AnimatedYouTubeSection>
                <YouTubeEmbed
                  videoId={heroVideo.id}
                  title={heroVideo.title}
                  channel={heroVideo.channel}
                  insights={heroVideo.insights}
                />
              </AnimatedYouTubeSection>
            )}

            {/* Key Stat Callout - quotable for AI */}
            {post.key_stat && (
              <KeyStatCallout stat={post.key_stat} />
            )}

            {/* Table of Contents - navigation for users and AI crawlers */}
            {post.toc && post.toc.length >= 3 && (
              <TableOfContents items={post.toc} />
            )}

            {/* Article Content - Scroll reveal */}
            <AnimatedArticleBody contentHtml={post.contentHtml || ''} />

            {/* Section YouTube Video (if present) - Scroll reveal */}
            {sectionVideo && (
              <ScrollRevealYouTube>
                <YouTubeEmbed
                  videoId={sectionVideo.id}
                  title={sectionVideo.title}
                  channel={sectionVideo.channel}
                  insights={sectionVideo.insights}
                />
              </ScrollRevealYouTube>
            )}

            {/* FAQ Section - structured for AI citation */}
            {post.faqs && post.faqs.length > 0 && (
              <FAQSection faqs={post.faqs} />
            )}

            {/* TL;DR Summary - quick reference for AI */}
            {post.tldr && (
              <TLDRSummary summary={post.tldr} />
            )}
          </div>

          {/* Printable Checklist - for step-by-step articles */}
          {post.howTo && (
            <PrintableChecklist title={post.title} steps={post.howTo.steps} />
          )}

          {/* Footer section with scroll animations */}
          <footer className="mt-12 pt-8 border-t border-gray-200 print:hidden">
            {/* Tags - Staggered reveal */}
            {post.tags && post.tags.length > 0 && (
              <AnimatedTags tags={post.tags} />
            )}

            {/* Share Buttons */}
            <ShareButtons url={`https://thegreenleaf.com/articles/${slug}`} title={post.title} />

            {/* Related Articles - Staggered reveal */}
            <AnimatedRelatedArticles posts={relatedPosts} />

            {/* CTA Section - Scroll reveal */}
            <AnimatedCTA />

            {/* Last Updated - freshness signal */}
            <LastUpdated date={post.last_updated || post.generated_at} />
          </footer>
        </div>
      </article>
    </>
  )
}
