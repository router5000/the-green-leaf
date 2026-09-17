"use client";

import Link from "next/link";
import { motion } from "motion/react";

const navLinks = [
  { label: "Home",     href: "/" },
  { label: "Topics",   href: "/topics" },
  { label: "Articles", href: "/articles" },
  { label: "Videos",   href: "/videos" },
];

const resourceLinks = [
  { label: "Strains",  href: "/strains" },
  { label: "Terpenes", href: "/terpenes" },
  { label: "States",   href: "/states" },
  { label: "About",    href: "/about" },
];

export default function Footer7() {
  return (
    <footer className="relative w-full px-4 sm:px-6 lg:px-8 py-12 sm:py-16" style={{ backgroundColor: '#f0f0f0' }}>
      <div className="relative max-w-[1400px] mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-[1.3fr_1fr_1fr_1fr] gap-10 lg:gap-8"
        >
          {/* Brand */}
          <div className="flex items-start gap-5">
            <img
              src="/images/logo/cannabis-logo.svg"
              alt="The Strain Report logo"
              width={72}
              height={72}
              style={{ width: '72px', height: '72px', flexShrink: 0 }}
            />
            <h3 className="text-2xl sm:text-3xl font-semibold text-neutral-900 leading-[1.05] tracking-tight">
              The Strain<br />Report
            </h3>
          </div>

          {/* Navigation */}
          <div className="flex flex-col gap-4">
            <h4 className="text-xs tracking-[0.2em] uppercase text-neutral-500">
              Navigation
            </h4>
            <ul className="flex flex-col gap-2 text-xl sm:text-2xl text-neutral-900">
              {navLinks.map((l) => (
                <li key={l.href}>
                  <Link href={l.href} className="hover:text-neutral-500 transition-colors no-underline">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div className="flex flex-col gap-4">
            <h4 className="text-xs tracking-[0.2em] uppercase text-neutral-500">
              Resources
            </h4>
            <ul className="flex flex-col gap-2 text-xl sm:text-2xl text-neutral-900">
              {resourceLinks.map((l) => (
                <li key={l.href}>
                  <Link href={l.href} className="hover:text-neutral-500 transition-colors no-underline">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Who We Are */}
          <div className="flex flex-col gap-4">
            <h4 className="text-xs tracking-[0.2em] uppercase text-neutral-500">
              Who We Are
            </h4>
            <p className="text-xl sm:text-2xl text-neutral-900 leading-tight">
              Your cannabis<br />education resource
            </p>
          </div>

        </motion.div>

        {/* Bottom bar: copyright/links left, medical disclaimer right (replaces email signup) */}
        <div className="mt-12 pt-8 border-t border-neutral-300 grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          <div className="flex flex-col gap-2 text-neutral-500 text-xs sm:text-sm">
            <p>© 2026 • The Strain Report • Cannabis education for everyone.</p>
            <div className="flex flex-wrap items-center gap-3">
              <Link href="/privacy-policy" className="hover:text-neutral-900 transition-colors no-underline">Privacy Policy</Link>
              <span className="text-neutral-400">•</span>
              <Link href="/terms-of-service" className="hover:text-neutral-900 transition-colors no-underline">Terms of Service</Link>
              <span className="text-neutral-400">•</span>
              <Link href="/affiliate-disclosure" className="hover:text-neutral-900 transition-colors no-underline">Affiliate Disclosure</Link>
            </div>
          </div>

          <p className="text-neutral-500 text-xs sm:text-sm leading-relaxed">
            Content on The Strain Report is for educational and informational purposes only and is
            not medical advice. It does not diagnose, treat, cure, or prevent any disease. Cannabis
            laws vary by jurisdiction — know your local laws. Always consult a qualified healthcare
            professional before using cannabis for any health-related purpose, especially if you are
            pregnant, nursing, take medications, or have a medical condition.
          </p>
        </div>
      </div>
    </footer>
  );
}
