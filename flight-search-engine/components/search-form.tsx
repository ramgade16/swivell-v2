"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { format } from "date-fns"
import { CalendarIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export function SearchForm() {
  const router = useRouter()
  const [departureAirport, setDepartureAirport] = useState("")
  const [arrivalAirport, setArrivalAirport] = useState("")
  const [date, setDate] = useState<Date | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(false)

  // Add these state variables after the existing ones
  const [numAdults, setNumAdults] = useState(1)
  const [numChildren, setNumChildren] = useState(0)
  const [checkedBag, setCheckedBag] = useState(false)

  // Update the handleSubmit function
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    // Format the date as YYYY-MM-DD
    const formattedDate = date ? format(date, "yyyy-MM-dd") : ""

    // Navigate to results page with query parameters
    router.push(
      `/results?from=${departureAirport}&to=${arrivalAirport}&date=${formattedDate}&adults=${numAdults}&children=${numChildren}&checkedBag=${checkedBag}`,
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="departureAirport">Departure Airport</Label>
          <Input
            id="departureAirport"
            placeholder="Enter airport code (e.g. LAX)"
            value={departureAirport}
            onChange={(e) => setDepartureAirport(e.target.value.toUpperCase())}
            maxLength={3}
            required
            className="uppercase"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="arrivalAirport">Arrival Airport</Label>
          <Input
            id="arrivalAirport"
            placeholder="Enter airport code (e.g. JFK)"
            value={arrivalAirport}
            onChange={(e) => setArrivalAirport(e.target.value.toUpperCase())}
            maxLength={3}
            required
            className="uppercase"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="date">Departure Date</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                id="date"
                variant="outline"
                className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date ? format(date, "PPP") : "Select date"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar mode="single" selected={date} onSelect={setDate} initialFocus />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {/* Add these form fields after the existing ones, before the submit button */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div className="space-y-2">
          <Label htmlFor="numAdults">Adults</Label>
          <Input
            id="numAdults"
            type="number"
            min="1"
            max="9"
            value={numAdults}
            onChange={(e) => setNumAdults(Number.parseInt(e.target.value) || 1)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="numChildren">Children</Label>
          <Input
            id="numChildren"
            type="number"
            min="0"
            max="9"
            value={numChildren}
            onChange={(e) => setNumChildren(Number.parseInt(e.target.value) || 0)}
          />
        </div>

        <div className="space-y-2 flex items-end">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="checkedBag"
              checked={checkedBag}
              onChange={(e) => setCheckedBag(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300"
            />
            <Label htmlFor="checkedBag">Checked Bag</Label>
          </div>
        </div>
      </div>

      <Button
        type="submit"
        className="w-full bg-skyblue-dark hover:bg-skyblue transition-colors duration-200 text-white font-medium"
        disabled={isLoading}
      >
        {isLoading ? "Searching..." : "Search Flights"}
      </Button>
    </form>
  )
}
