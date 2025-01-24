from fast_flights import FlightData, Passengers, Result, get_flights
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def fetch_with_timeout(func, *args, timeout=2, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)  # Enforce timeout
        except TimeoutError:
            print(f"Timed out while running {func.__name__} with args: {args}")
            return None

class FlightScraper:

    def __init__(self, ticket_type, departure_airport, arrival_airport, departure_date, arrival_date, num_adults, num_children, protected_price):
        self.ticket_type = ticket_type
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.departure_date = departure_date
        self.arrival_date = arrival_date
        self.num_adults = num_adults
        self.num_children = num_children
        self.protected_price = protected_price

    
    def search_flights(self):
        if self.protected_price == 0:
            try:
                results =  fetch_with_timeout(get_flights, flight_data=[
                            FlightData(date=self.departure_date, from_airport=self.departure_airport, to_airport=self.arrival_airport, max_stops=1)
                            ],
                            trip="one-way",
                            seat="economy",
                            passengers=Passengers(adults=int(self.num_adults), children=int(self.num_children), infants_in_seat=0, infants_on_lap=0),
                            fetch_mode="fallback",
                            timeout = 2
                            )
                if results is None:
                    return float("inf"), "hello"
                min_protected_price = 0
                flights = results.flights
                for i in range(min(10, len(flights))):
                    min_protected_price = max(min_protected_price, int(flights[i].price.replace("$", "")))
            
                return min_protected_price, "hello"
            except Exception as e:
                print(e)
                print(f"Couldn't find any valid flight options from {self.departure_airport} to {self.arrival_airport} on {self.departure_date}")
                return float("inf"), "hello"
            #return flights
        else:
            major_airports = ["ATL", "LAX", "DFW", "DEN", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"] 
            #["SEA", "EWR", "SFO", "PHX", "IAH", "BOS", "FLL", "MSP", "LGA", "DTW", "PHL", "SLC", "BWI", "DCA", "SAN", "IAD", "TPA", "BNA", "AUS", "MDW", "HNL", "DAL", "PDX", "STL", "RDU", "HOU", "OGG", "PIT", "MCI", "MSY", "PHL"]
            min_unprotected_price = float("inf")
            min_connecting_airport = ""
            for airport in major_airports:
                print(airport)
                min_first_leg = float("inf")
                min_second_leg = float("inf")
                if(airport != self.arrival_airport and airport != self.departure_airport):
                    try:
                        results = fetch_with_timeout(get_flights,flight_data=[
                                FlightData(date=self.departure_date, from_airport=self.departure_airport, to_airport=airport, max_stops=0)
                                ],
                                trip="one-way",
                                seat="economy",
                                passengers=Passengers(adults=int(self.num_adults), children=int(self.num_children), infants_in_seat=0, infants_on_lap=0),
                                fetch_mode="fallback",
                                timeout = 2
                                )
                        if results is None:
                            print(f"Timed out on {airport}")
                            continue
                        first_leg_flights = []
                        curr_price = 0
                        point_in_list = 0
                        while curr_price < self.protected_price and point_in_list < len(results.flights):
                            first_leg_flights.append(results.flights[point_in_list])
                            point_in_list += 1
                            min_first_leg = min(min_first_leg, int(flights[i].price.replace("$", "")))
                        results = None
                        results = fetch_with_timeout(get_flights, flight_data=[
                                FlightData(date=self.departure_date, from_airport=airport, to_airport=self.arrival_airport, max_stops=0)
                                ],
                                trip="one-way",
                                seat="economy",
                                passengers=Passengers(adults=int(self.num_adults), children=int(self.num_children), infants_in_seat=0, infants_on_lap=0),
                                fetch_mode="fallback",
                                timeout = 2
                                )
                        if results is None:
                            print(f"Timed out on {airport}")
                            continue
                        flights = results.flights
                        for i in range(min(5,len(flights))):
                            min_second_leg = min(min_second_leg, int(flights[i].price.replace("$", "")))
                        
                        if min_unprotected_price > min_first_leg + min_second_leg:
                            min_unprotected_price = min_first_leg + min_second_leg
                            min_connecting_airport = airport
                    except Exception:
                        continue

                    
            if(self.protected_price + 150 > min_unprotected_price):
                return min_unprotected_price, min_connecting_airport
            else:
                return 0, "hello"
            #return flights
                    

                
                
        
    #build priority queue for best SWIVELL flight choices
        

    

# print(result.flights[0].price)

# # The price is currently... low/typical/high
# print("The price is currently", result.current_price)