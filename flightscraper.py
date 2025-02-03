from fast_flights import FlightData, Passengers, Result, get_flights
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timedelta

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

    def parse_time(self, time_str):
        time_part = time_str.split(" on ")[0]
        dt = datetime.strptime(time_part, "%I:%M %p")
        dt = dt.replace(year=1970, month=1, day=1)
        return dt

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
                min_protected_price = float("inf") # maybe consider changing to max logic
                flights = results.flights
                direct_flight_results=[]
                for i in range(min(10, len(flights))):
                    min_protected_price = min(min_protected_price, int(flights[i].price.replace("$", ""))) # maybe consider changing to max logic
                    direct_flight_results.append(flights[i])
            
                return direct_flight_results, min_protected_price
            except Exception as e:
                print(e)
                print(f"Couldn't find any valid flight options from {self.departure_airport} to {self.arrival_airport} on {self.departure_date}")
                return float("inf"), "hello"
            #return flights
        else:
            major_airports = ["ATL", "LAX", "DFW", "DEN", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"] 
            #["ATL", "LAX", "DFW", "DEN", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"] 
            #["SEA", "EWR", "SFO", "PHX", "IAH", "BOS", "FLL", "MSP", "LGA", "DTW", "PHL", "SLC", "BWI", "DCA", "SAN", "IAD", "TPA", "BNA", "AUS", "MDW", "HNL", "DAL", "PDX", "STL", "RDU", "HOU", "OGG", "PIT", "MCI", "MSY", "PHL"]
            min_unprotected_price = float("inf")
            final_flight_results = []
            for airport in major_airports:
                print(airport)
                min_first_leg = float("inf")
                # min_second_leg = float("inf")
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
                        min_first_leg_arrival = self.parse_time("11:59 PM on Thu, Jan 30")

                        for first_leg in results.flights:
                            if(int(first_leg.price.replace("$", "")) < self.protected_price):
                                first_leg_flights.append(first_leg)
                                min_first_leg = min(min_first_leg, int(first_leg.price.replace("$", "")))
                                min_first_leg_arrival = min(min_first_leg_arrival, self.parse_time(first_leg.arrival))
                        
                        # if min_first_leg_arrival > self.parse_time("10:30 PM on Thu, Jan 30"):
                        #     continue


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
                        for second_leg in results.flights:
                            if(self.parse_time(second_leg.departure) >= min_first_leg_arrival + timedelta(hours=2) and int(second_leg.price.replace("$", "")) + min_first_leg <= self.protected_price + 200):
                                for first_leg in first_leg_flights:
                                    if(self.parse_time(second_leg.departure) >= self.parse_time(first_leg.departure) + timedelta(hours = 2) and int(first_leg.price.replace("$", "")) + int(second_leg.price.replace("$", "")) <= self.protected_price + 200):
                                        final_flight_results.append((first_leg, second_leg))
                                        min_unprotected_price = min(min_unprotected_price, int(first_leg.price.replace("$", "")) + int(second_leg.price.replace("$", "")))

                    except Exception:
                        continue

                    
            return final_flight_results, min_unprotected_price
            #return flights
                    

                
                
        
    #build priority queue for best SWIVELL flight choices
        

    

# print(result.flights[0].price)

# # The price is currently... low/typical/high
# print("The price is currently", result.current_price)