from fast_flights import FlightData, Passengers, Result, get_flights
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timedelta
import heapq

def fetch_with_timeout(func, *args, timeout=2, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)  # Enforce timeout
        except TimeoutError:
            print(f"Timed out while running {func.__name__} with args: {args}")
            return None

class FlightScraper:

    def __init__(self):
        print("Hello! I hope you're ready to book some flights!")
    
    def askUserForFlightDetails(self):
        self.ticket_type = input("Will you be flying One-Way or Round-Trip? (Answer with an \"O\" or \"R\") --> ")
        self.departure_airport = input("Which airport will you be flying from today? Please enter the airport's 3-letter code (e.g. \"LAX\") --> ")
        self.arrival_airport = input("Which airport will you be flying to today?  Please enter the airport's 3-letter code (e.g. \"ORD\") -->  ")
        self.departure_date = input("What is your departure date? Please enter in this format: \"2025-01-01\" --> ")
        if(self.ticket_type == "R"):
            self.arrival_date = input("What is your arrival date? Please enter in this format: \"Sunday, January 26,\" --> ")
        else:
            self.arrival_date = "NA"
        self.num_adults = input("How many adults will be travelling?  --> ")
        self.num_children = input("How many children will be travelling? --> ")
        self.checked_bag = (input("Will you be flying with a checked bag today? (Answer with an \"Y\" or \"N\") --> ") == "Y")
        self.max_protected_price = 0
        self.max_protected_duration = 0
        self.max_unprotected_price = 0
        self.max_unprotected_duration = 0
        print("Searching protected flights.")


    def parse_time(self, time_str):
        time_part = time_str.split(" on ")[0]
        dt = datetime.strptime(time_part, "%I:%M %p")
        dt = dt.replace(year=1970, month=1, day=1)
        return dt

    def search_protected_flights(self):
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
            min_protected_price = float("inf")
            flights = results.flights
            protected_flight_results=[]
            for i in range(min(10, len(flights))):
                if int(flights[i].price.replace("$", "")) != 0:
                    min_protected_price = min(min_protected_price, int(flights[i].price.replace("$", "")))
                    self.max_protected_price = max(self.max_protected_price, int(flights[i].price.replace("$", "")))
                    duration_hours = flights[i].duration.split()[0]
                    duration_minutes = flights[i].duration.split()[2]
                    self.max_protected_duration = max(self.max_protected_duration, (60 * duration_hours) + duration_minutes)
                    protected_flight_results.append(flights[i])
            
            return protected_flight_results, min_protected_price
        except Exception as e:
            print(e)
            print(f"Couldn't find any valid flight options from {self.departure_airport} to {self.arrival_airport} on {self.departure_date}")
            return float("inf"), "hello"
        #return flights
    

    def search_unprotected_flights(self, min_protected_price):
        major_airports = ["ATL", "FLL", "IAH", "PHX", "BNA", "IAD","PHL", "LGA", "BWI", "MDW", "LAX", "DFW", "DEN", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"] 
        #["ATL", "LAX", "DFW", "DEN", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"] 
        #["SEA", "EWR", "SFO", "PHX", "IAH", "BOS", "FLL", "MSP", "LGA", "DTW", "PHL", "SLC", "BWI", "DCA", "SAN", "IAD", "TPA", "BNA", "AUS", "MDW", "HNL", "DAL", "PDX", "STL", "RDU", "HOU", "OGG", "PIT", "MCI", "MSY", "PHL"]
        min_unprotected_price = float("inf")
        unprotected_flight_results = []
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
                        if(int(first_leg.price.replace("$", "")) != 0 and int(first_leg.price.replace("$", "")) < min_protected_price):
                            first_leg_flights.append((self.parse_time(first_leg.arrival), first_leg))
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
                    first_leg_flights = sorted(first_leg_flights, key=lambda x: x[0])

                    layover_hours = 0
                    if self.checked_bag:
                        layover_hours = 3
                    else:
                        layover_hours = 2

                    for second_leg in results.flights:
                        if(int(second_leg.price.replace("$", ""))!=0 and int(second_leg.price.replace("$", "")) + min_first_leg <= min_protected_price + 200):
                            curr_position = 0
                            while(curr_position < len(first_leg_flights) and self.parse_time(second_leg.departure) >= first_leg_flights[curr_position][0] + timedelta(hours = layover_hours)):
                                first_leg = first_leg_flights[curr_position][1]
                                if (int(first_leg.price.replace("$", "")) + int(second_leg.price.replace("$", "")) <= min_protected_price+ 200):
                                    unprotected_flight_results.append((airport, first_leg, second_leg))
                                    min_unprotected_price = min(min_unprotected_price, int(first_leg.price.replace("$", "")) + int(second_leg.price.replace("$", "")))
                                curr_position += 1

                except Exception:
                    continue

                    
        return unprotected_flight_results, min_unprotected_price
        #return flights
    
    def displaying_priority(self, normalized_price, normalized_duration):
        return (0.5 * normalized_price) + (0.5 * normalized_duration)
    
    def display_recommended_flights(self, final_flight_results, bool_protected):
        flights_pq = []

        if bool_protected:
            for flight_option in final_flight_results:
                price = int(flight_option.price.replace("$", ""))
                duration_hours = flight_option.duration.split()[0]
                duration_minutes = flight_option.duration_split()[2]
                duration = (60 * duration_hours) + duration_minutes
                priority_score = self.displaying_priority(price/self.max_protected_price, duration/self.max_protected_duration)
                heapq.heappush(flights_pq, (priority_score, flight_option))
        # else:
        #     for _, first_leg, second_leg in final_flight_results:
        #         first_leg_price = first_leg.price
        #         second_leg_price = second_leg.price
        #         layover = self.parse_time(second_leg.departure) - self.parse_time(first_leg.departure)
        
        if bool_protected:
            print("These are the top 10 recommended protected flight options by SWIVELL:")
        else:
            print("These are the top 10 recommended unprotected flight options by SWIVELL:")
        
        i = 0
        while flights_pq and i < 10:
            _, flight_option = heapq.heappop(flights_pq)
            print(flight_option)

                
                
        
    #build priority queue for best SWIVELL flight choices
        

    

# print(result.flights[0].price)
# # The price is currently... low/typical/high
# print("The price is currently", result.current_price)