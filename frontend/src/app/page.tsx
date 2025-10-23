export default function Home() {
  return (
    <main className="space-y-6">
      <h1 className="text-5xl font-extrabold">Cross-Domain Review Intelligence</h1>
      <p className="opacity-80">Transfer insights from health/drug reviews to general products. Search similar experiences. Explain model decisions.</p>
      <div className="grid md:grid-cols-3 gap-4">
        <a className="rounded-2xl p-6 bg-white/10 hover:bg-white/15" href="/dashboard">Dashboard</a>
        <a className="rounded-2xl p-6 bg-white/10 hover:bg-white/15" href="/search">Similar Experiences</a>
        <a className="rounded-2xl p-6 bg-white/10 hover:bg-white/15" href="/explain">Explain a Prediction</a>
      </div>
    </main>
  );
}
