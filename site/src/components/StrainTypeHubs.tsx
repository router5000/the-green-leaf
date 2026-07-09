import Link from 'next/link';

export default function StrainTypeHubs() {
  return (
    <section className="py-12 px-4 sm:px-6 lg:px-8 bg-[#f0f0f0]">
      <div className="max-w-[1400px] mx-auto w-full">
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-8">
          Explore by Strain Type
        </h2>
        <div className="grid gap-6 sm:grid-cols-3">
          <Link
            href="/strains/indica"
            className="block bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="h-48 bg-gradient-to-b from-green-100 to-green-200 flex items-center justify-center">
              <span className="text-2xl font-semibold text-gray-800">Indica</span>
            </div>
          </Link>
          <Link
            href="/strains/sativa"
            className="block bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="h-48 bg-gradient-to-b from-green-100 to-green-200 flex items-center justify-center">
              <span className="text-2xl font-semibold text-gray-800">Sativa</span>
            </div>
          </Link>
          <Link
            href="/strains/hybrid"
            className="block bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="h-48 bg-gradient-to-b from-green-100 to-green-200 flex items-center justify-center">
              <span className="text-2xl font-semibold text-gray-800">Hybrid</span>
            </div>
          </Link>
        </div>
      </div>
    </section>
  );
}