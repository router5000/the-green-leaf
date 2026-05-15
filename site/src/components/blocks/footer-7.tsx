"use client";

import Link from "next/link";
import { motion } from "motion/react";

const exploreLinks = [
  { label: "Home", href: "/" },
  { label: "Topics", href: "/topics" },
  { label: "Articles", href: "/articles" },
  { label: "Videos", href: "/videos" },
];

const contentLinks = [
  { label: "Strain Reviews", href: "/articles?tab=strain-reviews" },
  { label: "By Effect", href: "/articles?tab=by-effect" },
  { label: "Indica / Sativa / Hybrid", href: "/articles?tab=indica-sativa" },
  { label: "Science & Education", href: "/articles?tab=science" },
];

const legalLinks = [
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Terms of Service", href: "/terms" },
  { label: "Affiliate Disclosure", href: "/affiliate" },
  { label: "Legal Disclaimer", href: "/legal" },
];

export default function Footer7() {
  return (
    <footer className="relative w-full pl-4 sm:pl-6 md:pl-28 pr-4 sm:pr-6 lg:pr-8 py-12 sm:py-16 bg-white border-t border-gray-200 print:hidden">
      <div className="relative max-w-[1400px] mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-[1.3fr_1fr_1fr_1fr] gap-10 lg:gap-8"
        >
          {/* Brand column */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-4">
              <div className="shrink-0 w-12 h-12 rounded-full bg-leaf-600" />
              <h3 className="text-2xl font-semibold text-leaf-900 leading-tight tracking-tight">
                The Green<br />Leaf
              </h3>
            </div>
            <p className="text-sm text-gray-500 leading-relaxed max-w-xs">
              In-depth strain reviews, effect guides, and cannabis education.
            </p>
          </div>

          {/* Explore column */}
          <div className="flex flex-col gap-4">
            <h4 className="text-xs tracking-[0.2em] uppercase text-gray-400">
              Explore
            </h4>
            <ul className="flex flex-col gap-2 text-lg text-gray-800">
              {exploreLinks.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="hover:text-leaf-600 transition-colors no-underline"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Content column */}
          <div className="flex flex-col gap-4">
            <h4 className="text-xs tracking-[0.2em] uppercase text-gray-400">
              Content
            </h4>
            <ul className="flex flex-col gap-2 text-lg text-gray-800">
              {contentLinks.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="hover:text-leaf-600 transition-colors no-underline"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal column */}
          <div className="flex flex-col gap-4">
            <h4 className="text-xs tracking-[0.2em] uppercase text-gray-400">
              Legal
            </h4>
            <ul className="flex flex-col gap-2 text-lg text-gray-800">
              {legalLinks.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="hover:text-leaf-600 transition-colors no-underline"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </motion.div>

        <div className="mt-16 grid grid-cols-1 lg:grid-cols-2 gap-8 items-end">
          <p className="text-gray-400 text-xs sm:text-sm">
            © 2026 The Green Leaf. Content is for educational purposes only.
          </p>

          <div>
            <h4 className="text-xs tracking-[0.2em] uppercase text-gray-400 mb-3">
              Stay informed
            </h4>
            <form className="flex items-center rounded-full border border-gray-300 bg-white p-1.5">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 min-w-0 bg-transparent rounded-full px-5 py-2 text-gray-900 text-sm placeholder:text-gray-400 focus:outline-none"
              />
              <button
                type="submit"
                className="rounded-full bg-leaf-600 text-white px-5 py-2.5 text-xs tracking-[0.1em] uppercase font-medium hover:bg-leaf-700 transition-colors cursor-pointer whitespace-nowrap"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>
      </div>
    </footer>
  );
}
