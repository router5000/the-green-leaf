import Link from 'next/link';

export default function TopicQuickLinks() {
  const topics = [
    { label: 'Growing', slug: 'growing' },
    { label: 'Consumption', slug: 'consumption' },
    { label: 'Wellness', slug: 'wellness' },
    { label: 'Legal', slug: 'legal' },
    { label: 'Culture', slug: 'culture' },
  ];

  return (
    <section className="py-12 px-4 sm:px-6 lg:px-8 bg-[#f0f0f0]">
      <div className="max-w-[1400px] mx-auto w-full">
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-gray-900 mb-8">
          Popular Topics
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {topics.map((topic) => (
            <Link
              key={topic.slug}
              href={`/topics/${topic.slug}`}
              className="block bg-white rounded-lg p-4 text-center hover:bg-gray-50 transition-colors"
            >
              <span className="font-medium text-gray-900">{topic.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}