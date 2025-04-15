import { NextResponse } from "next/server"
import { exec } from "child_process"
import { promisify } from "util"

const execPromise = promisify(exec)

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const from = searchParams.get("from")
  const to = searchParams.get("to")
  const date = searchParams.get("date")
  const adults = searchParams.get("adults") || "1"
  const children = searchParams.get("children") || "0"
  const checkedBag = searchParams.get("checkedBag") || "false"

  console.log(
    `API Request: from=${from}, to=${to}, date=${date}, adults=${adults}, children=${children}, checkedBag=${checkedBag}`,
  )

  if (!from || !to || !date) {
    return NextResponse.json({ error: "Missing required parameters" }, { status: 400 })
  }

  try {
    // Execute the Python script with the search parameters
    console.log(`Executing Python script with params: ${from} ${to} ${date} ${adults} ${children} ${checkedBag}`)

    const { stdout, stderr } = await execPromise(
      `python api/flight_api.py ${from} ${to} ${date} ${adults} ${children} ${checkedBag}`,
      { maxBuffer: 1024 * 1024 * 10 }, // Increase buffer size to 10MB
    )

    if (stderr) {
      console.error("Python script error:", stderr)
      return NextResponse.json({ error: "Error executing flight search" }, { status: 500 })
    }

    // Parse the JSON output from the Python script
    try {
      const results = JSON.parse(stdout)
      console.log(
        `API Results: ${results.protectedFlights?.length || 0} protected flights, ${results.unprotectedFlights?.length || 0} unprotected flights`,
      )
      return NextResponse.json(results)
    } catch (parseError) {
      console.error("Error parsing Python script output:", parseError)
      console.log("Raw output:", stdout)
      return NextResponse.json({ error: "Invalid response format from flight search" }, { status: 500 })
    }
  } catch (error) {
    console.error("Error executing Python script:", error)
    return NextResponse.json({ error: "Failed to search flights" }, { status: 500 })
  }
}
