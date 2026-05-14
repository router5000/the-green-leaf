'use client'

import { motion, useReducedMotion } from 'framer-motion'
import Link from 'next/link'
import Image from 'next/image'
import { ReactNode, useState } from 'react'

// Reusable scroll-triggered animation wrapper
export function ScrollReveal({
  children,
  delay = 0,
  className = ''
}: {
  children: ReactNode
  delay?: number
  className?: string
}) {
  const shouldReduceMotion = useReducedMotion()
  return (
    <motion.div
      className={className}
      initial={shouldReduceMotion ? false : { opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.5, delay, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )
}

// Page load animation for hero section
export function HeroImage({
  src,
  alt
}: {
  src: string
  alt: string
}) {
  const shouldReduceMotion = useReducedMotion()
  return (
    <motion.figure
      className="relative h-56 sm:h-72 md:h-96 w-full mb-8 overflow-hidden"
      initial={shouldReduceMotion ? false : { opacity: 0, scale: 1.05 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.7, ease: "easeOut" }}
      itemProp="image"
    >
      <Image
        src={src}
        alt={alt}
        fill
        className="object-cover"
        priority
        sizes="100vw"
        itemProp="url"
      />
      <motion.div
        className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      />
    </motion.figure>
  )
}

// Animated breadcrumb navigation
export function AnimatedBreadcrumb({ title, category }: { title: string; category?: string }) {
  const shouldReduceMotion = useReducedMotion()
  return (
    <motion.nav
      className="text-sm text-gray-500 mb-8"
      aria-label="Breadcrumb"
      initial={shouldReduceMotion ? false : { opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: shouldReduceMotion ? 0 : 0.4, delay: shouldReduceMotion ? 0 : 0.2 }}
    >
      <Link href="/" className="hover:text-leaf-600">Home</Link>
      <span className="mx-2">/</span>
      <Link href="/articles" className="hover:text-leaf-600">Articles</Link>
      {category && (
        <>
          <span className="mx-2">/</span>
          <Link href="/topics" className="hover:text-leaf-600">{category}</Link>
        </>
      )}
      <span className="mx-2">/</span>
      <span className="text-leaf-700">{title}</span>
    </motion.nav>
  )
}

// Inline share icons for article header
function InlineShareIcons({ url, title }: { url: string; title: string }) {
  const [copied, setCopied] = useState(false)
  const encodedUrl = encodeURIComponent(url)
  const encodedTitle = encodeURIComponent(title)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      const input = document.createElement('input')
      input.value = url
      document.body.appendChild(input)
      input.select()
      document.execCommand('copy')
      document.body.removeChild(input)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="flex items-center gap-1.5 ml-auto print:hidden">
      <a
        href={`https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`}
        target="_blank"
        rel="noopener noreferrer"
        className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100"
        aria-label="Share on Twitter"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      </a>
      <a
        href={`https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`}
        target="_blank"
        rel="noopener noreferrer"
        className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100"
        aria-label="Share on Facebook"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
      </a>
      <a
        href={`https://www.linkedin.com/shareArticle?mini=true&url=${encodedUrl}&title=${encodedTitle}`}
        target="_blank"
        rel="noopener noreferrer"
        className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100"
        aria-label="Share on LinkedIn"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
      </a>
      <button
        onClick={handleCopy}
        className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100"
        aria-label={copied ? 'Link copied' : 'Copy link'}
      >
        {copied ? (
          <svg className="w-4 h-4 text-leaf-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg>
        ) : (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
        )}
      </button>
    </div>
  )
}

// Animated article header
export function AnimatedHeader({
  season,
  readTime,
  wordCount,
  title,
  description,
  generatedAt,
  slug
}: {
  season: string
  readTime: string
  wordCount: number
  title: string
  description: string
  generatedAt: string
  slug: string
}) {
  return (
    <motion.header
      className="mb-10"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <div className="flex flex-wrap items-center gap-3 text-sm text-leaf-600 mb-4">
        <motion.span
          className="bg-leaf-100 px-3 py-1 rounded-full font-medium"
          itemProp="articleSection"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          {season}
        </motion.span>
        <time itemProp="timeRequired">{readTime}</time>
        <span className="text-gray-400">•</span>
        <span itemProp="wordCount">{wordCount} words</span>
        <InlineShareIcons url={`https://thegreenleaf.com/articles/${slug}`} title={title} />
      </div>

      <motion.h1
        className="text-2xl sm:text-3xl md:text-4xl font-bold text-leaf-900 mb-4"
        itemProp="headline"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        {title}
      </motion.h1>

      <motion.p
        className="text-xl text-gray-600"
        itemProp="description"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        {description}
      </motion.p>

      {/* Hidden metadata for AI crawlers */}
      <meta itemProp="datePublished" content={generatedAt} />
      <meta itemProp="dateModified" content={generatedAt} />
      <meta itemProp="inLanguage" content="en-US" />
      <meta itemProp="author" content="The Green Leaf" />
    </motion.header>
  )
}

// Animated article body with scroll reveal
export function AnimatedArticleBody({ contentHtml }: { contentHtml: string }) {
  return (
    <ScrollReveal>
      <div
        className="prose prose-lg max-w-none prose-img:rounded-xl prose-img:shadow-md prose-headings:scroll-mt-20"
        itemProp="articleBody"
        dangerouslySetInnerHTML={{ __html: contentHtml }}
      />
    </ScrollReveal>
  )
}

// Animated tags section
export function AnimatedTags({ tags }: { tags: string[] }) {
  return (
    <ScrollReveal delay={0.1}>
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Tags:</h3>
        <div className="flex flex-wrap gap-2">
          {tags?.map((tag, index) => (
            <motion.span
              key={tag}
              className="bg-leaf-100 text-leaf-700 px-3 py-1 rounded-full text-sm"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              {tag}
            </motion.span>
          ))}
        </div>
      </div>
    </ScrollReveal>
  )
}

// Animated related articles
interface RelatedPost {
  slug: string
  season: string
  estimated_read_time: string
  title: string
  meta_description: string
  featured_image?: string
  featured_image_alt?: string
}

export function AnimatedRelatedArticles({ posts }: { posts: RelatedPost[] }) {
  if (posts.length === 0) return null

  return (
    <ScrollReveal delay={0.15}>
      <div className="mb-8">
        <h3 className="text-xl font-bold text-leaf-900 mb-6">
          Related Articles
        </h3>
        <div className="grid md:grid-cols-3 gap-5">
          {posts.map((post, index) => (
            <motion.div
              key={post.slug}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <Link
                href={`/articles/${post.slug}`}
                className="group block bg-white border border-gray-200 rounded-xl overflow-hidden hover:border-leaf-500 hover:shadow-lg transition-all"
              >
                {post.featured_image && (
                  <div className="relative aspect-[16/9] overflow-hidden bg-gray-100">
                    <Image
                      src={post.featured_image}
                      alt={post.featured_image_alt || post.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                      sizes="(max-width: 768px) 100vw, 33vw"
                    />
                  </div>
                )}
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-leaf-100 text-leaf-700 px-2 py-0.5 rounded text-xs font-medium capitalize">
                      {post.season}
                    </span>
                    <span className="text-xs text-gray-500">
                      {post.estimated_read_time}
                    </span>
                  </div>
                  <h4 className="font-semibold text-leaf-900 group-hover:text-leaf-700 mb-2 line-clamp-2 text-sm">
                    {post.title}
                  </h4>
                  <p className="text-xs text-gray-600 line-clamp-2">
                    {post.meta_description}
                  </p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </ScrollReveal>
  )
}

// Animated CTA section
export function AnimatedCTA() {
  return (
    <ScrollReveal delay={0.2}>
      <div className="bg-leaf-50 rounded-lg p-6">
        <h3 className="font-semibold text-leaf-900 mb-2">
          Keep Your Cannabis Thriving
        </h3>
        <p className="text-gray-600 mb-4">
          Explore more expert guides and seasonal tips to maintain your perfect cannabis.
        </p>
        <Link
          href="/articles"
          className="text-leaf-600 hover:text-leaf-800 font-medium"
        >
          ← Browse All Articles
        </Link>
      </div>
    </ScrollReveal>
  )
}

// Animated YouTube embed wrapper
export function AnimatedYouTubeSection({ children, delay = 0 }: { children: ReactNode, delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 + delay }}
    >
      {children}
    </motion.div>
  )
}

// Scroll-triggered YouTube section
export function ScrollRevealYouTube({ children }: { children: ReactNode }) {
  return (
    <ScrollReveal delay={0.1}>
      <div className="mt-8 min-h-[280px]">
        <h3 className="text-lg font-semibold text-leaf-800 mb-4">Related Video</h3>
        {children}
      </div>
    </ScrollReveal>
  )
}

// Table of Contents - auto-generated from headings
interface TocItem {
  id: string
  text: string
  level: number
}

export function TableOfContents({ items }: { items: TocItem[] }) {
  if (!items || items.length < 3) return null

  return (
    <ScrollReveal>
      <nav className="my-8 bg-gray-50 rounded-xl p-5 md:p-6 border border-gray-200" aria-label="Table of Contents">
        <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
          In This Article
        </h2>
        <ul className="space-y-1.5">
          {items.map((item) => (
            <li key={item.id} className={item.level === 3 ? 'pl-4' : ''}>
              <a
                href={`#${item.id}`}
                className="text-sm text-leaf-700 hover:text-leaf-900 hover:underline transition-colors block py-0.5"
              >
                {item.text}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </ScrollReveal>
  )
}

// Key Stat Callout - quotable statistic for AI citation
export function KeyStatCallout({ stat }: { stat: string }) {
  if (!stat) return null

  // Rotate between labels based on stat content for variety
  const labels = ['Pro Tip', 'Key Takeaway', 'Fast Fact']
  const hash = stat.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  const label = labels[hash % labels.length]

  return (
    <ScrollReveal>
      <div className="my-8 bg-gradient-to-r from-leaf-50 to-emerald-50 border-l-4 border-leaf-500 rounded-r-lg p-6 shadow-sm">
        <p className="text-sm font-semibold text-leaf-700 uppercase tracking-wide mb-2">
          {label}
        </p>
        <p className="text-lg font-medium text-gray-800 leading-relaxed">
          {stat}
        </p>
      </div>
    </ScrollReveal>
  )
}

// TL;DR Summary - bottom of article for quick reference
export function TLDRSummary({ summary }: { summary: string }) {
  if (!summary) return null

  return (
    <ScrollReveal>
      <div className="my-8 bg-gray-100 border border-gray-200 rounded-lg p-5">
        <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">
          TL;DR
        </p>
        <p className="text-base text-gray-800 leading-relaxed">
          {summary}
        </p>
      </div>
    </ScrollReveal>
  )
}

// Last Updated display
export function LastUpdated({ date }: { date: string }) {
  if (!date) return null

  const formatted = new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  return (
    <p className="text-sm text-gray-500 mt-4">
      Last updated: <time dateTime={date}>{formatted}</time>
    </p>
  )
}

// Helper to render step text with proper list formatting
function StepText({ text }: { text: string }) {
  const lines = text.split('\n')
  const listItems: string[] = []
  const paragraphs: string[] = []

  for (const line of lines) {
    if (/^\d+\.\s+/.test(line)) {
      listItems.push(line.replace(/^\d+\.\s+/, ''))
    } else if (/^[-*]\s+/.test(line)) {
      listItems.push(line.replace(/^[-*]\s+/, ''))
    } else {
      paragraphs.push(line)
    }
  }

  const renderInline = (str: string) => {
    const parts = str.split(/\*\*(.+?)\*\*/)
    return parts.map((part, i) =>
      i % 2 === 1 ? <strong key={i}>{part}</strong> : <span key={i}>{part}</span>
    )
  }

  return (
    <div className="text-sm text-gray-600 mt-0.5 print:text-gray-800">
      {paragraphs.length > 0 && <p>{renderInline(paragraphs.join(' '))}</p>}
      {listItems.length > 0 && (
        <ul className="mt-1 ml-4 space-y-0.5 list-disc">
          {listItems.map((item, i) => (
            <li key={i}>{renderInline(item)}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

// Printable Checklist - for HowTo articles
interface ChecklistStep {
  name: string
  text: string
}

export function PrintableChecklist({ title, steps }: { title: string; steps: ChecklistStep[] }) {
  if (!steps || steps.length < 2) return null

  const handlePrint = () => {
    window.print()
  }

  return (
    <ScrollReveal>
      <div className="my-10 border border-gray-200 rounded-xl overflow-hidden print:border-none print:my-0">
        {/* Screen header */}
        <div className="flex items-center justify-between bg-leaf-50 px-5 py-4 border-b border-gray-200 print:bg-white print:border-b-2 print:border-black print:py-2">
          <h3 className="font-bold text-leaf-900 text-lg print:text-black print:text-xl">
            Checklist: {title}
          </h3>
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 bg-leaf-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-leaf-700 transition-colors print:hidden"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Print Checklist
          </button>
        </div>
        {/* Steps */}
        <div className="p-5 space-y-4 print:p-0 print:pt-4">
          {steps.map((step, index) => (
            <label key={index} className="flex items-start gap-3 cursor-pointer group">
              <input
                type="checkbox"
                className="mt-1 w-5 h-5 rounded border-gray-300 text-leaf-600 focus:ring-leaf-500 print:w-4 print:h-4 shrink-0"
              />
              <div>
                <span className="font-semibold text-gray-900 group-hover:text-leaf-700 transition-colors print:text-black">
                  {index + 1}. {step.name}
                </span>
                <StepText text={step.text} />
              </div>
            </label>
          ))}
        </div>
        {/* Print footer */}
        <div className="hidden print:block border-t border-gray-300 pt-3 mt-4 text-xs text-gray-500">
          <p>thegreenleaf.com - Your complete cannabis resource</p>
        </div>
      </div>
    </ScrollReveal>
  )
}

// FAQ Section with collapsible answers
interface FAQItem {
  question: string
  answer: string
}

export function FAQSection({ faqs }: { faqs: FAQItem[] }) {
  if (!faqs || faqs.length === 0) return null

  return (
    <ScrollReveal>
      <div className="my-10 bg-gray-50 rounded-xl p-6 md:p-8">
        <h2 className="text-2xl font-bold text-leaf-900 mb-6">
          Frequently Asked Questions
        </h2>
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.details
              key={index}
              className="group bg-white rounded-lg border border-gray-200 overflow-hidden"
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <summary className="flex items-center justify-between cursor-pointer p-4 hover:bg-leaf-50 transition-colors">
                <h3 className="font-semibold text-gray-900 pr-4">{faq.question}</h3>
                <span className="text-leaf-600 group-open:rotate-180 transition-transform">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </span>
              </summary>
              <div className="px-4 pb-4 text-gray-700 leading-relaxed border-t border-gray-100 pt-3">
                {faq.answer}
              </div>
            </motion.details>
          ))}
        </div>
      </div>
    </ScrollReveal>
  )
}
