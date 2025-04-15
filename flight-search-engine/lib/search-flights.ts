// Replace the mock implementation with actual API calls

export async function searchFlights(
  from: string,
  to: string,
  date: string,
  adults = 1,
  children = 0,
  checkedBag = false,
) {
  try {
    // Build the query string
    const params = new URLSearchParams({
      from,
      to,
      date,
      adults: adults.toString(),
      children: children.toString(),
      checkedBag: checkedBag.toString(),
    })

    console.log(`Calling API with params: ${params.toString()}`)

    // Call the API endpoint
    const response = await fetch(`/api/search?${params.toString()}`)

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    console.log("Raw API response:", data)

    // If there's an error in the response
    if (data.error) {
      throw new Error(data.error)
    }

    return {
      protectedFlights: data.protectedFlights || [],
      unprotectedFlights: data.unprotectedFlights || [],
    }
  } catch (error) {
    console.error("Error searching flights:", error)
    // Return empty arrays in case of error
    return {
      protectedFlights: [],
      unprotectedFlights: [],
    }
  }
}
