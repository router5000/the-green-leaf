"use client";

import { useState, useRef } from "react";
import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  AnimatePresence,
} from "motion/react";
import { Home, Briefcase, User, Mail, Menu, X } from "lucide-react";

export function Navigation4() {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const mouseY = useMotionValue<number>(Infinity);

  const navItems = [
    { id: "home", icon: Home, label: "Home", href: "#" },
    { id: "works", icon: Briefcase, label: "Works", href: "#" },
    { id: "profile", icon: User, label: "Profile", href: "#" },
    { id: "contact", icon: Mail, label: "Contact", href: "#" },
  ];

  return (
    <div className="min-h-screen w-full flex bg-white dark:bg-neutral-950">
      {/* Mobile Navigation - Top Brand */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
        className="md:hidden fixed top-0 left-0 right-0 z-50 px-6 py-4"
      >
        <div className="flex items-center justify-between">
          <div className="text-left">
            <p className="text-sm font-bold text-neutral-900 dark:text-white leading-tight">
              Brand
            </p>
            <p className="text-sm font-bold text-neutral-900 dark:text-white leading-tight">
              Appart
            </p>
          </div>

          {/* Hamburger Menu */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="flex h-10 w-10 items-center justify-center rounded-md bg-neutral-900 dark:bg-white text-white dark:text-neutral-900"
            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </div>
      </motion.div>

      {/* Mobile Bottom Dock */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.nav
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            className="md:hidden fixed bottom-3 left-0 right-0 z-50 px-4 pb-6"
          >
            <motion.div className="flex items-center justify-center gap-4 px-6 py-4 rounded-3xl bg-white/80 backdrop-blur-2xl dark:bg-neutral-900/80 border border-neutral-200/50 dark:border-neutral-800/50 shadow-xl mx-auto w-fit">
              {navItems.map((item, index) => (
                <MobileNavItem key={item.id} item={item} index={index} />
              ))}
            </motion.div>
          </motion.nav>
        )}
      </AnimatePresence>

      {/* Side Navigation - Desktop Only */}
      <motion.nav
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="hidden md:flex fixed left-0 top-0 h-screen w-24 flex-col items-center py-8"
      >
        {/* Logo */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.4, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
          className="mb-12"
        >
          <div className="w-14 h-14 rounded-full bg-neutral-900 dark:bg-white"></div>
        </motion.div>

        {/* Nav Items Container */}
        <motion.div
          className="flex-1 flex flex-col items-center justify-center gap-4"
          onMouseMove={(e) => mouseY.set(e.pageY)}
          onMouseLeave={() => mouseY.set(Infinity)}
        >
          {navItems.map((item, index) => (
            <NavItem
              key={item.id}
              item={item}
              index={index}
              mouseY={mouseY}
              hoveredItem={hoveredItem}
              setHoveredItem={setHoveredItem}
            />
          ))}
        </motion.div>

        {/* Brand Text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.8 }}
          className="mt-8"
        >
          <div className="text-left">
            <p className="text-sm font-bold text-neutral-900 dark:text-white leading-tight">
              Build
            </p>
            <p className="text-sm font-bold text-neutral-900 dark:text-white leading-tight">
              Better
            </p>
          </div>
        </motion.div>
      </motion.nav>
    </div>
  );
}

interface NavItemProps {
  item: {
    id: string;
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    href: string;
  };
  index: number;
  mouseY: ReturnType<typeof useMotionValue<number>>;
  hoveredItem: string | null;
  setHoveredItem: (id: string | null) => void;
}

function NavItem({
  item,
  index,
  mouseY,
  hoveredItem,
  setHoveredItem,
}: NavItemProps) {
  const ref = useRef<HTMLDivElement>(null);
  const Icon = item.icon;

  const distance = useTransform(mouseY, (val: number) => {
    const bounds = ref.current?.getBoundingClientRect() ?? { y: 0, height: 0 };
    return val - bounds.y - bounds.height / 2;
  });

  const sizeTransform = useTransform(
    distance,
    [-150, -75, 0, 75, 150],
    [56, 60, 64, 60, 56],
  );

  const size = useSpring(sizeTransform, {
    mass: 0.1,
    stiffness: 150,
    damping: 12,
  });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.3,
        delay: 0.3 + index * 0.1,
        ease: [0.4, 0, 0.2, 1],
      }}
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
      onMouseEnter={() => setHoveredItem(item.id)}
      onMouseLeave={() => setHoveredItem(null)}
    >
      <a
        href={item.href}
        className="flex items-center justify-center w-full h-full rounded-2xl bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 no-underline"
      >
        <Icon className="w-5 h-5 text-neutral-900 dark:text-white" />
      </a>

      {/* Tooltip */}
      <AnimatePresence>
        {hoveredItem === item.id && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute left-full ml-4 top-1/2 -translate-y-1/2 whitespace-nowrap px-3 py-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-white text-sm font-medium shadow-lg"
          >
            {item.label}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

interface MobileNavItemProps {
  item: {
    id: string;
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    href: string;
  };
  index: number;
}

function MobileNavItem({ item, index }: MobileNavItemProps) {
  const Icon = item.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        duration: 0.3,
        delay: 0.3 + index * 0.1,
        ease: [0.4, 0, 0.2, 1],
      }}
      className="relative flex items-center justify-center w-12 h-12"
    >
      <a
        href={item.href}
        className="flex items-center justify-center w-full h-full rounded-2xl bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 no-underline"
      >
        <Icon className="w-5 h-5 text-neutral-900 dark:text-white" />
      </a>
    </motion.div>
  );
}

export default Navigation4;
