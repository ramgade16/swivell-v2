"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FlightCard } from "@/components/flight-card"
import { searchFlights } from "@/lib/search-flights"
import { Loader2 } from "lucide-react"

interface Flight {
  id: string
  airlines: string[]
  departureAirport: string
  arrivalAirport: string
  departureTime: string
  arrivalTime: string
  duration: string
  price: number
  stops: number
  layoverAirport?: string
  isProtected: boolean
  legs?: Flight[]
}

export function FlightResults({
  from,
  to,
  date,
  adults = 1,
  children = 0,
  checkedBag = false,
}: {
  from: string
  to: string
  date: string
  adults?: number
  children?: number
  checkedBag?: boolean
}) {
  const [loading, setLoading] = useState(true)
  const [protectedFlights, setProtectedFlights] = useState<Flight[]>([])
  const [unprotectedFlights, setUnprotectedFlights] = useState<Flight[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchFlights = async () => {
      try {
        setLoading(true)
        setError(null)

        console.log(`Searching flights from ${from} to ${to} on ${date}`)
        const results = await searchFlights(from, to, date, adults, children, checkedBag)

        console.log("API Results:", results)
        console.log("Protected flights:", results.protectedFlights?.length || 0)
        console.log("Unprotected flights:", results.unprotectedFlights?.length || 0)

        if (results.protectedFlights) {
          setProtectedFlights(results.protectedFlights)
        }

        if (results.unprotectedFlights) {
          setUnprotectedFlights(results.unprotectedFlights)
        }
      } catch (error) {
        console.error("Error fetching flights:", error)
        setError("Failed to fetch flight data. Please try again.")
      } finally {
        setLoading(false)
      }
    }

    fetchFlights()
  }, [from, to, date, adults, children, checkedBag])

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Searching for the best flights...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center py-20 text-red-500">
        <p>{error}</p>
      </div>
    )
  }

  return (
    <Tabs defaultValue="protected">
      <TabsList className="grid w-full grid-cols-2 mb-6 bg-gray-100">
        <TabsTrigger value="protected" className="data-[state=active]:bg-white data-[state=active]:text-skyblue-dark">
          Protected Flights ({protectedFlights.length})
        </TabsTrigger>
        <TabsTrigger value="unprotected" className="data-[state=active]:bg-white data-[state=active]:text-skyblue-dark">
          Unprotected Flights ({unprotectedFlights.length})
        </TabsTrigger>
      </TabsList>

      <TabsContent value="protected" className="space-y-4">
        {protectedFlights.length === 0 ? (
          <p className="text-center py-10 text-muted-foreground">No protected flights found for this route.</p>
        ) : (
          protectedFlights.map((flight) => <FlightCard key={flight.id} flight={flight} />)
        )}
      </TabsContent>

      <TabsContent value="unprotected" className="space-y-4">
        {unprotectedFlights.length === 0 ? (
          <p className="text-center py-10 text-muted-foreground">No unprotected flights found for this route.</p>
        ) : (
          unprotectedFlights.map((flight) => <FlightCard key={flight.id} flight={flight} />)
        )}
      </TabsContent>
    </Tabs>
  )
}
