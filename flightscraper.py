
from fast_flights import FlightData, Passengers, Result, get_flights

class FlightScraper:

    def __init__(self, ticket_type, departure_airport, arrival_airport, departure_date, arrival_date):
        self.ticket_type = ticket_type
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.departure_date = departure_date
        self.arrival_date = arrival_date

result: Result = get_flights(
    flight_data=[
        FlightData(date="2025-02-01", from_airport="HSV", to_airport="ORD")
    ],
    trip="one-way",
    seat="economy",
    passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
    fetch_mode="fallback",
)

print(result.flights[0].price)

# The price is currently... low/typical/high
print("The price is currently", result.current_price)