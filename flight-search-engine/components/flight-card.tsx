"use client"

import { useState } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ChevronDown, ChevronUp, Clock, ExternalLink } from "lucide-react"
import { cn } from "@/lib/utils"

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

export function FlightCard({ flight }: { flight: Flight }) {
  const [isHovered, setIsHovered] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  const formatDuration = (duration: string) => {
    // Convert "X hr Y min" format to display
    return duration
  }

  const getAirlineLogo = (airline: string) => {
    // Map airline names to their logo paths
    const airlineLogos: Record<string, string> = {
      Emirates: "/images/airlines/emirates.png",
      Southwest: "/images/airlines/southwest.png",
      Delta: "/images/airlines/delta.png",
      United: "/images/airlines/united.png",
      American: "/images/airlines/american.png",
      Alaska: "/images/airlines/alaska.png",
      Spirit: "/images/airlines/spirit.png",
      Allegiant: "/images/airlines/allegiant.png",
      Etihad: "/images/airlines/etihad.png",
      Frontier: "/images/airlines/frontier.png",
      Hawaiian: "/images/airlines/hawaiian.png",
      JetBlue: "/images/airlines/jetblue.png",
    }

    return airlineLogos[airline] || "/images/airlines/generic.png"
  }

  // function generateExpediaUrl(
  //   departureAirport: string,
  //   arrivalAirport: string,
  //   departureDate: string, // Must be "YYYY-MM-DD"
  //   numAdults = 1,
  //   maxStops: number | null = null // 0 for nonstop, 1 for one-stop, null for any
  // ) {
  //   const baseUrl = `https://www.expedia.com/Flights-Search?trip=oneway`
  //   const legPart = `&leg1=from:${departureAirport},to:${arrivalAirport},departure:${departureDate}TANYT`
  //   const passengerPart = `&passengers=adults:${numAdults}`
  //   const options = `&options=cabinclass:economy${maxStops !== null ? `,stops:${maxStops}` : ""}`
  
  //   return `${baseUrl}${legPart}${passengerPart}${options}&mode=search`.replace(/\s+/g, "")
  // } FIX THISSSSSS/IMPLEMENT IT

  return (
    <Card
      className={cn(
        "transition-all duration-200 border border-gray-200",
        isHovered ? "shadow-md border-l-4 border-l-skyblue" : "hover:border-l-2 hover:border-l-skyblue-light",
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardContent className="p-4">
        <div className="flex flex-col space-y-4">
          {/* Main flight info */}
          <div className="grid grid-cols-12 gap-2 items-center">
            {/* Airline logo */}
            <div className="col-span-1">
              <div className="relative h-10 w-10">
                <Image
                  src={getAirlineLogo(flight.airlines[0]) || "/placeholder.svg"}
                  alt={flight.airlines[0]}
                  fill
                  className="object-contain"
                />
              </div>
            </div>

            {/* Airline name */}
            <div className="col-span-2">
              <p className="text-sm font-medium">{flight.airlines.join(", ")}</p>
            </div>

            {/* Departure */}
            <div className="col-span-2 text-center">
              <p className="text-lg font-bold">{flight.departureTime}</p>
              <p className="text-xs text-muted-foreground">{flight.departureAirport}</p>
            </div>

            {/* Duration/stops */}
            <div className="col-span-3 flex flex-col items-center">
              <p className="text-xs text-muted-foreground">{formatDuration(flight.duration)}</p>
              <div className="w-full h-[2px] bg-gray-300 my-1 relative">
                {flight.stops > 0 && (
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-gray-500 rounded-full" />
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {flight.stops === 0 ? "Nonstop" : `${flight.stops} stop${flight.stops > 1 ? "s" : ""}`}
                {flight.layoverAirport && ` (${flight.layoverAirport})`}
              </p>
            </div>

            {/* Arrival */}
            <div className="col-span-2 text-center">
              <p className="text-lg font-bold">{flight.arrivalTime}</p>
              <p className="text-xs text-muted-foreground">{flight.arrivalAirport}</p>
            </div>

            {/* Price */}
            <div className="col-span-2 text-right">
              <p className="text-2xl font-bold text-green-600">${flight.price}</p>
              {isHovered && (
                <Button
                  size="sm"
                  className="mt-1 bg-skyblue hover:bg-skyblue-dark transition-colors duration-200"
                  asChild
                >
                  <a href="#" target="_blank" rel="noopener noreferrer">
                    Book Flight <ExternalLink className="ml-1 h-3 w-3" />
                  </a>
                </Button>
              )}
            </div>
          </div>

          {/* Connection details for unprotected flights */}
          {!flight.isProtected && flight.legs && flight.legs.length > 0 && (
            <div>
              <Button
                variant="ghost"
                size="sm"
                className="w-full flex items-center justify-center text-skyblue-dark hover:text-purple-dark"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? (
                  <>
                    Hide details <ChevronUp className="ml-1 h-4 w-4" />
                  </>
                ) : (
                  <>
                    Show connection details <ChevronDown className="ml-1 h-4 w-4" />
                  </>
                )}
              </Button>

              {isExpanded && (
                <div className="mt-2 space-y-4 border-t pt-4">
                  {flight.legs.map((leg, index) => (
                    <div key={index} className="grid grid-cols-12 gap-2 items-center">
                      <div className="col-span-1">
                        <div className="relative h-8 w-8">
                          <Image
                            src={getAirlineLogo(leg.airlines[0]) || "/placeholder.svg"}
                            alt={leg.airlines[0]}
                            fill
                            className="object-contain"
                          />
                        </div>
                      </div>

                      <div className="col-span-2">
                        <p className="text-xs font-medium">{leg.airlines.join(", ")}</p>
                        <p className="text-xs text-muted-foreground">Leg {index + 1}</p>
                      </div>

                      <div className="col-span-2 text-center">
                        <p className="text-sm font-medium">{leg.departureTime}</p>
                        <p className="text-xs text-muted-foreground">{leg.departureAirport}</p>
                      </div>

                      <div className="col-span-3 flex flex-col items-center">
                        <p className="text-xs text-muted-foreground">{formatDuration(leg.duration)}</p>
                        <div className="w-full h-[2px] bg-gray-300 my-1" />
                        <p className="text-xs text-muted-foreground">
                          <Clock className="inline h-3 w-3 mr-1" />
                          {formatDuration(leg.duration)}
                        </p>
                      </div>

                      <div className="col-span-2 text-center">
                        <p className="text-sm font-medium">{leg.arrivalTime}</p>
                        <p className="text-xs text-muted-foreground">{leg.arrivalAirport}</p>
                      </div>

                      {isHovered && (
                        <div className="col-span-2 text-right">
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-skyblue text-skyblue-dark hover:bg-skyblue/10"
                            asChild
                          >
                            <a href="#" target="_blank" rel="noopener noreferrer">
                              Book This Leg <ExternalLink className="ml-1 h-3 w-3" />
                            </a>
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
