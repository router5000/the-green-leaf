export default function FooterSitemapLinks() {
  return (
    <footer className="bg-gray-900 text-gray-200 py-8">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid gap-6 sm:grid-cols-3">
          <div>
            <h3 className="mb-4 font-semibold text-white">Main Sections</h3>
            <ul className="space-y-2">
              <li><a href="/strains" className="hover:text-white transition-colors">Strains</a></li>
              <li><a href="/articles" className="hover:text-white transition-colors">Articles</a></li>
              <li><a href="/topics" className="hover:text-white transition-colors">Topics</a></li>
              <li><a href="/videos" className="hover:text-white transition-colors">Videos</a></li>
              <li><a href="/about" className="hover:text-white transition-colors">About</a></li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 font-semibold text-white">Strain Types</h3>
            <ul className="space-y-2">
              <li><a href="/strains/indica" className="hover:text-white transition-colors">Indica</a></li>
              <li><a href="/strains/sativa" className="hover:text-white transition-colors">Sativa</a></li>
              <li><a href="/strains/hybrid" className="hover:text-white transition-colors">Hybrid</a></li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 font-semibold text-white">Legal</h3>
            <ul className="space-y-2">
              <li><a href="/privacy-policy" className="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="/terms-of-service" className="hover:text-white transition-colors">Terms of Service</a></li>
              <li><a href="/affiliate-disclosure" className="hover:text-white transition-colors">Affiliate Disclosure</a></li>
            </ul>
          </div>
        </div>
        <p className="mt-8 text-center text-gray-500 text-sm">
          © {new Date().getFullYear()} StrainReport. All rights reserved.
        </p>
      </div>
    </footer>
  );
}