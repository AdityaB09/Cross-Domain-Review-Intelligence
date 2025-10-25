export default function Home() {
  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900">
          Cross-Domain Review Intelligence
        </h1>
        <p className="max-w-2xl text-base text-gray-600">
          Transfer insights from health/drug reviews to general products.
          Search similar experiences. Explain model decisions.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <a
          href="/dashboard"
          className="rounded-2xl border bg-white p-6 shadow-sm hover:shadow-md hover:bg-gray-50 transition"
        >
          <div className="text-lg font-semibold text-gray-900">Dashboard</div>
          <div className="text-sm text-gray-600">
            System health, index status, sentiment trends.
          </div>
        </a>

        <a
          href="/search"
          className="rounded-2xl border bg-white p-6 shadow-sm hover:shadow-md hover:bg-gray-50 transition"
        >
          <div className="text-lg font-semibold text-gray-900">Similar Experiences</div>
          <div className="text-sm text-gray-600">
            Ask a question. Retrieve semantically similar reviews.
          </div>
        </a>

        <a
          href="/explain"
          className="rounded-2xl border bg-white p-6 shadow-sm hover:shadow-md hover:bg-gray-50 transition"
        >
          <div className="text-lg font-semibold text-gray-900">Explain a Prediction</div>
          <div className="text-sm text-gray-600">
            Aspect-based sentiment + token highlights.
          </div>
        </a>
      </div>
    </section>
  );
}
