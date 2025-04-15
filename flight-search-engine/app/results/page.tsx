import { Suspense } from "react"
import { FlightResults } from "@/components/flight-results"
import { BackgroundGradient } from "@/components/background-gradient"
import { Skeleton } from "@/components/ui/skeleton"

export default async function ResultsPage({
  searchParams,
}: {
  searchParams: {
    from: string
    to: string
    date: string
    adults?: string
    children?: string
    checkedBag?: string
  }
}) {
  // In Next.js 15, we need to await searchParams before using it
  const params = await Promise.resolve(searchParams)
  const { from, to, date, adults = "1", children = "0", checkedBag = "false" } = params

  return (
    <main className="min-h-screen flex flex-col">
      <BackgroundGradient />
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <h1 className="text-2xl font-bold mb-2 text-gray-800">Flight Results</h1>
          <p className="text-skyblue-dark mb-6">
            {from} to {to} • {date} • {adults} Adult{Number(adults) !== 1 ? "s" : ""}
            {Number(children) > 0 ? `, ${children} Child${Number(children) !== 1 ? "ren" : ""}` : ""}
          </p>
          <Suspense fallback={<ResultsSkeleton />}>
            <FlightResults
              from={from}
              to={to}
              date={date}
              adults={Number.parseInt(adults)}
              children={Number.parseInt(children)}
              checkedBag={checkedBag === "true"}
            />
          </Suspense>
        </div>
      </div>
    </main>
  )
}

function ResultsSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-10 w-[300px]" />
        <div className="grid gap-4">
          {Array(3)
            .fill(0)
            .map((_, i) => (
              <Skeleton key={i} className="h-[120px] w-full" />
            ))}
        </div>
      </div>
    </div>
  )
}
