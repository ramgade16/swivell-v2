import { SearchForm } from "@/components/search-form"
import { BackgroundGradient } from "@/components/background-gradient"

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <BackgroundGradient />
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-center mb-2 text-gray-800">SWIVELL</h1>
          <p className="text-xl text-center mb-8 text-gray-600">Connecting Flights. Connecting Cities. Connecting The World.</p>
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <SearchForm />
          </div>
        </div>
      </div>
    </main>
  )
}
