"use client";

import Link from "next/link";
import { motion, useMotionValue, useAnimationFrame } from "motion/react";
import { useRef, useState, useEffect } from "react";
import { resolveArticleImage } from "@/lib/articleImage";

const CATEGORY_LABELS: Record<string, string> = {
  'strains-genetics':    'Strains & Genetics',
  'growing-cultivation': 'Growing & Cultivation',
  'consumption-methods': 'Consumption Methods',
  'health-wellness':     'Health & Wellness',
  'legal-industry':      'Legal & Industry',
  'culture-lifestyle':   'Culture & Lifestyle',
};

const SHOWCASE_ITEMS = [
  {
    id: 1,
    slug: 'blue-dream-strain-effects-review',
    featured_image: '/images/articles/blue-dream-strain-effects-review.jpg',
    title: 'Blue Dream Strain Effects & Review (2024)',
    category: 'strains-genetics',
    height: 'h-[400px]',
  },
  {
    id: 2,
    slug: 'best-strains-for-anxiety-and-stress',
    featured_image: '/images/articles/best-strains-for-anxiety-and-stress.jpg',
    title: 'Best Strains for Anxiety and Stress in 2025',
    category: 'strains-genetics',
    height: 'h-[450px]',
  },
  {
    id: 3,
    slug: 'cannabis-consumption-methods-compared',
    featured_image: '/images/articles/cannabis-consumption-methods-compared.jpg',
    title: 'Cannabis Consumption Methods Compared (2024 Guide)',
    category: 'consumption-methods',
    height: 'h-[420px]',
  },
  {
    id: 4,
    slug: 'how-to-germinate-cannabis-seeds',
    featured_image: '/images/articles/how-to-germinate-cannabis-seeds.jpg',
    title: 'How to Germinate Cannabis Seeds (5 Easy Methods)',
    category: 'growing-cultivation',
    height: 'h-[380px]',
  },
  {
    id: 5,
    slug: 'organic-cannabis-soil-preparation',
    featured_image: '/images/articles/organic-cannabis-soil-preparation.jpg',
    title: 'Organic Cannabis Soil Preparation Guide (2024)',
    category: 'growing-cultivation',
    height: 'h-[430px]',
  },
];

export function Showcase2() {
  const [isDragging, setIsDragging] = useState(false);
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const [oneSetWidth, setOneSetWidth] = useState(0);

  const baseVelocity = -20;
  const baseX = useMotionValue(0);
  const scrollVelocity = useRef(baseVelocity);
  const scrollerRef = useRef<HTMLDivElement>(null);

  const items = [
    ...SHOWCASE_ITEMS, ...SHOWCASE_ITEMS, ...SHOWCASE_ITEMS,
    ...SHOWCASE_ITEMS, ...SHOWCASE_ITEMS, ...SHOWCASE_ITEMS,
  ];

  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 640;
      const itemWidth = isMobile ? 280 : 320;
      const gap = 24;
      const width = (itemWidth + gap) * SHOWCASE_ITEMS.length;
      setOneSetWidth(width);
      baseX.set(-width);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [baseX]);

  useAnimationFrame((_t, delta) => {
    if (!oneSetWidth) return;
    if (!isDragging) {
      scrollVelocity.current = scrollVelocity.current * 0.9 + baseVelocity * 0.1;
      const moveBy = scrollVelocity.current * (delta / 1000);
      baseX.set(baseX.get() + moveBy);
      const x = baseX.get();
      if (x <= -oneSetWidth * 2) { baseX.set(x + oneSetWidth); }
      else if (x > 0) { baseX.set(x - oneSetWidth); }
    }
  });

  return (
    <section className="w-full py-12 px-4 sm:px-6 lg:px-8" style={{ backgroundColor: '#f0f0f0' }}>
      <div className="max-w-[1400px] mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="max-w-xl">
            <p className="text-sm sm:text-base text-neutral-600 mb-4">
              Latest Articles
            </p>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-medium tracking-tight text-neutral-900 leading-[1.15] mb-8 sm:mb-10">
              Cannabis knowledge,<br className="hidden sm:block" /> expertly researched.
            </h2>
            <Link href="/articles">
              <motion.span
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="inline-block px-8 py-3.5 rounded-full text-white font-medium text-sm sm:text-base transition-colors duration-200 no-underline"
                style={{ backgroundColor: '#1a3a0a' }}
              >
                View All Articles
              </motion.span>
            </Link>
          </div>
        </motion.div>

        <div className="relative -mx-4 sm:-mx-6 lg:-mx-8 overflow-hidden py-20">
          <motion.div
            ref={scrollerRef}
            className="flex items-end gap-6 cursor-grab active:cursor-grabbing"
            style={{ x: baseX }}
            drag="x"
            onDragStart={() => setIsDragging(true)}
            onDragEnd={(_e, info) => {
              setIsDragging(false);
              scrollVelocity.current = info.velocity.x;
            }}
            dragElastic={0.05}
            dragMomentum={false}
          >
            {items.map((item, index) => (
              <Link
                key={`${item.id}-${index}`}
                href={`/articles/${item.slug}`}
                className="no-underline"
                draggable={false}
                onClick={(e) => { if (isDragging) e.preventDefault(); }}
              >
                <motion.div
                  className={`shrink-0 w-[280px] sm:w-[320px] ${item.height} rounded-2xl overflow-hidden select-none relative pointer-events-auto`}
                  initial={{ rotateX: 0, opacity: 1 }}
                  animate={
                    hoveredId === index
                      ? { scale: 1.05, rotateX: -15, y: -25, zIndex: 50 }
                      : { scale: 1, rotateX: 0, y: 0, zIndex: 1 }
                  }
                  transition={{
                    duration: 0.3,
                    ease: 'backOut',
                    zIndex: { delay: hoveredId === index ? 0 : 0.4 },
                  }}
                  onMouseEnter={() => setHoveredId(index)}
                  onMouseLeave={() => setHoveredId(null)}
                  style={{ transformPerspective: 1000 }}
                >
                  <div className="w-full h-full bg-green-900/30 relative">
                    <img
                      src={resolveArticleImage(item, item.id - 1)}
                      alt={item.title}
                      width={320}
                      height={400}
                      loading="lazy"
                      decoding="async"
                      className="w-full h-full object-cover object-top pointer-events-none"
                      draggable={false}
                    />
                    {/* Gradient overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent pointer-events-none" />
                    {/* Article info */}
                    <div className="absolute bottom-0 left-0 right-0 p-4">
                      <p className="text-xs font-medium uppercase tracking-wide mb-1" style={{ color: '#4a8c2a' }}>
                        {CATEGORY_LABELS[item.category] ?? item.category}
                      </p>
                      <p className="text-white text-sm font-medium leading-snug line-clamp-2">
                        {item.title}
                      </p>
                    </div>
                  </div>
                </motion.div>
              </Link>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
