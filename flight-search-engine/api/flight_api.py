import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Import your existing code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.flightscraper import FlightScraper

class FlightAPI:
    def __init__(self):
        self.scraper = FlightScraper()
    
    def search_flights(self, departure_airport: str, arrival_airport: str, 
                      departure_date: str, num_adults: int = 1, 
                      num_children: int = 0, checked_bag: bool = False) -> Dict[str, Any]:
        """
        Search for flights and return results in JSON format
        """
        # Set the flight details without prompting
        self.scraper.departure_airport = departure_airport
        self.scraper.arrival_airport = arrival_airport
        self.scraper.departure_date = departure_date
        self.scraper.num_adults = str(num_adults)
        self.scraper.num_children = str(num_children)
        self.scraper.checked_bag = checked_bag
        
        # Search for protected flights
        protected_flights, min_protected_price = self.scraper.search_protected_flights()
        
        # Search for unprotected flights
        unprotected_flights, min_unprotected_price = self.scraper.search_unprotected_flights(min_protected_price)
        
        # Format the results for the frontend
        formatted_protected = self._format_protected_flights(protected_flights)
        formatted_unprotected = self._format_unprotected_flights(unprotected_flights)
        
        return {
            "protectedFlights": formatted_protected,
            "unprotectedFlights": formatted_unprotected,
            "minProtectedPrice": min_protected_price if min_protected_price != float("inf") else None,
            "minUnprotectedPrice": min_unprotected_price if min_unprotected_price != float("inf") else None
        }
    
    def _format_protected_flights(self, flights: List[Any]) -> List[Dict[str, Any]]:
        """
        Format protected flights for the frontend
        """
        formatted_flights = []
        
        for i, flight in enumerate(flights):
            formatted_flight = {
                "id": f"p{i+1}",
                "airlines": flight.airlines,
                "departureAirport": self.scraper.departure_airport,
                "arrivalAirport": self.scraper.arrival_airport,
                "departureTime": flight.departure_time,
                "arrivalTime": flight.arrival_time,
                "duration": f"{int(flight.duration_in_minutes/60)} hr {flight.duration_in_minutes % 60} min",
                "price": flight.price,
                "stops": flight.num_stops,
                "isProtected": True
            }
            formatted_flights.append(formatted_flight)
        
        return formatted_flights
    
    def _format_unprotected_flights(self, flight_tuples: List[Tuple]) -> List[Dict[str, Any]]:
        """
        Format unprotected flights for the frontend
        """
        formatted_flights = []
        
        try:
            for i, flight_tuple in enumerate(flight_tuples):
                # Check if the tuple has the expected structure
                if len(flight_tuple) != 4:
                    print(f"Warning: Unexpected tuple format at index {i}: {flight_tuple}")
                    continue
                
                total_option, first_leg, second_leg, layover_airport = flight_tuple
                
                # Format the main flight
                formatted_flight = {
                    "id": f"u{i+1}",
                    "airlines": total_option.airlines,
                    "departureAirport": self.scraper.departure_airport,
                    "arrivalAirport": self.scraper.arrival_airport,
                    "departureTime": first_leg.departure_time,
                    "arrivalTime": second_leg.arrival_time,
                    "duration": f"{int(total_option.duration_in_minutes/60)} hr {total_option.duration_in_minutes % 60} min",
                    "price": total_option.price,
                    "stops": 1,
                    "layoverAirport": layover_airport,
                    "isProtected": False,
                    "legs": [
                        {
                            "id": f"u{i+1}-1",
                            "airlines": first_leg.airlines,
                            "departureAirport": self.scraper.departure_airport,
                            "arrivalAirport": layover_airport,
                            "departureTime": first_leg.departure_time,
                            "arrivalTime": first_leg.arrival_time,
                            "duration": f"{int(first_leg.duration_in_minutes/60)} hr {first_leg.duration_in_minutes % 60} min",
                            "price": first_leg.price,
                            "stops": 0,
                            "isProtected": False
                        },
                        {
                            "id": f"u{i+1}-2",
                            "airlines": second_leg.airlines,
                            "departureAirport": layover_airport,
                            "arrivalAirport": self.scraper.arrival_airport,
                            "departureTime": second_leg.departure_time,
                            "arrivalTime": second_leg.arrival_time,
                            "duration": f"{int(second_leg.duration_in_minutes/60)} hr {second_leg.duration_in_minutes % 60} min",
                            "price": second_leg.price,
                            "stops": 0,
                            "isProtected": False
                        }
                    ]
                }
                formatted_flights.append(formatted_flight)
        except Exception as e:
            print(f"Error formatting unprotected flights: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return formatted_flights

def main():
    """
    Command-line interface for the Flight API
    """
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Missing required parameters"}))
        sys.exit(1)
    
    departure_airport = sys.argv[1]
    arrival_airport = sys.argv[2]
    departure_date = sys.argv[3]
    
    num_adults = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    num_children = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    checked_bag = sys.argv[6].lower() == "true" if len(sys.argv) > 6 else False
    
    api = FlightAPI()
    results = api.search_flights(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_date=departure_date,
        num_adults=num_adults,
        num_children=num_children,
        checked_bag=checked_bag
    )
    
    # Print the results as JSON
    print(json.dumps(results))

if __name__ == "__main__":
    main()
