from fast_flights import FlightData, Passengers, Result, get_flights
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timedelta
from ranker import XGBoostRanker
import heapq
import pandas as pd
from dataclasses import dataclass


import os
from supabase import create_client, Client
url = "https://rbdpujuypscjtdmddydc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJiZHB1anV5cHNjanRkbWRkeWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMxNDQ2MTIsImV4cCI6MjA1ODcyMDYxMn0.fLF-cTy1uYFKd5Y_N8X9Bi03e9K4yurRksdjFajwBss"
supabase: Client = create_client(url, key)

def fetch_with_timeout(func, *args, timeout=5, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)  # Enforce timeout
        except TimeoutError:
            print(f"Timed out while running {func.__name__} with args: {args}")
            return None

@dataclass
class FlightOption:
    # initializes the flight option instance
    def __init__(self, price, num_stops, duration_in_minutes, departure_time, arrival_time, airlines, is_multi_airline):
        self.price = price
        self.num_stops = num_stops
        self.duration_in_minutes = duration_in_minutes
        self.departure_time = departure_time
        self.arrival_time = arrival_time

        # representing this as a list here
        self.airlines = airlines
        self.is_multi_airline = is_multi_airline

        

class FlightScraper:

    # initializes the scraper instance
    def __init__(self):
        print("Hello! I hope you're ready to book some flights!")

        self.ranker = XGBoostRanker(
            model_path='xgboost_model.json',
            learning_rate=0.1,
            n_estimators=100
        )
        self.ranker.train()

        self.protected_flight_results = []
        self.unprotected_flight_results = []
    
    # prompts the user for their travel details
    def askUserForFlightDetails(self):
        self.ticket_type = input("Will you be flying One-Way or Round-Trip? (Answer with an \"O\" or \"R\") --> ")
        self.departure_airport = input("Which airport will you be flying from today? Please enter the airport's 3-letter code (e.g. \"LAX\") --> ")
        self.arrival_airport = input("Which airport will you be flying to today?  Please enter the airport's 3-letter code (e.g. \"ORD\") -->  ")
        self.departure_date = input("What is your departure date? Please enter in this format: \"2025-01-01\" --> ")
        if(self.ticket_type == "R"):
            self.arrival_date = input("What is your arrival date? Please enter in this format: \"Sunday, January 26,\" --> ")
        else:
            self.arrival_date = None
        self.num_adults = input("How many adults will be travelling?  --> ")
        self.num_children = input("How many children will be travelling? --> ")
        self.checked_bag = (input("Will you be flying with a checked bag today? (Answer with an \"Y\" or \"N\") --> ") == "Y")
        self.max_protected_price = 0
        self.max_protected_duration = 0
        self.max_unprotected_price = 0
        self.max_unprotected_duration = 0
        print("Searching protected flights.")
    
    # saves each flight query to the supabase
    def save_flight_query_to_db(self, departure_airport, arrival_airport, departure_date, num_passengers):
        try:
            response = supabase.table("flight_queries").insert({
                "origin_airport": departure_airport,
                "destination_airport": arrival_airport,
                "departure_date": departure_date,
                "num_passengers": num_passengers
            }).execute()

            query_id = response.data[0]["query_id"]
            return query_id
        except Exception as e:
            print(f"Connection Error: {e}")
    
    # saves the flight results to the supabase
    def save_flight_results_to_db(self, query_id, rank_in_results, flight_price, num_stops, duration_minutes, departure_time, arrival_time, airlines, is_multi_airline):
        try:
            supabase.table("flight_query_results").insert({
                "query_id": query_id,
                "rank_in_results": rank_in_results,
                "flight_price": flight_price,
                "num_stops": num_stops,
                "duration_minutes": duration_minutes,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "airlines": airlines,
                "is_multi_airline": is_multi_airline,
            }).execute()

        except Exception as e:
            print(f"Connection Error: {e}")
    

    def rank_flights(self, flights_of_interest, is_protected):
    # 1. Convert your flights into a DataFrame
    #    Make sure the columns line up with how your model was trained!
    #    Suppose flights_for_query is a list of flight objects with fields:
    #       - price (int)
    #       - num_stops (int)
    #       - duration_minutes (int)
    #       - departure_time (str, e.g. "6:30 AM")
    #       - arrival_time (str, e.g. "11:05 AM")
    #       - is_multi_airline (bool)

        if is_protected:
            flights_for_ranking = flights_of_interest
        else:
            flights_for_ranking = [flight_tuple[0] for flight_tuple in flights_of_interest]
        
        if not flights_for_ranking:
            return []  # or handle the empty case appropriately
    
        df = pd.DataFrame([
            {
                "flight_price": flight.price, 
                "num_stops": flight.num_stops, 
                "duration_minutes": flight.duration_in_minutes,
                "departure_time": flight.departure_time,
                "arrival_time": flight.arrival_time,
                "airlines": flight.airlines[0] if not flight.is_multi_airline else f"{flight.airlines[0]}, {flight.airlines[1]}",
                "is_multi_airline": 1 if flight.is_multi_airline else 0,
                "query_id": 0
            } 
            for flight in flights_for_ranking
        ])
        
        new_df = self.ranker.preprocess_data(df)
       
        X = new_df[["flight_price", 
                "num_stops", 
                "duration_minutes", 
                "departure_sin", 
                "departure_cos", 
                "arrival_sin", 
                "arrival_cos",
                "airlines",
                "is_multi_airline"]]
        
        # 7. Predict
        predictions = self.ranker.predict(X)
        
        # 8. Sort flights by descending predicted score
        df["score"] = predictions
        df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)

        # 9. Re-map the sorted DataFrame rows back to the original flights
        #    Typically you'd store an index in df so you can do this easily:
        df_sorted["original_index"] = df_sorted.index
        ranked_flights = [flights_of_interest[i] for i in df_sorted.index]

        return ranked_flights



    def parse_time(self, time_str):
        time_part = time_str.split(" on ")[0]
        dt = datetime.strptime(time_part, "%I:%M %p")
        dt = dt.replace(year=1970, month=1, day=1)
        return dt
    
    def process_time(self, flight_duration):
        # check if duration is in the form hrs and mins or just hrs or just mins. extract the duration accordingly
        duration_parts = flight_duration.split() 

        # duration is in the form hrs and mins
        if len(duration_parts) == 4:
            duration_in_minutes = (60 * int(duration_parts[0])) + int(duration_parts[2])
        elif len(duration_parts) == 2:
            # duration is in the form just mins
            if duration_parts[1] == "min":
                duration_in_minutes = int(duration_parts[0])
            # duration is in the form just hours
            else:
                duration_in_minutes = 60 * int(duration_parts[0])
            
        return duration_in_minutes
    
    # searches the protected flight options(provided by Google Flights)
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
            
            # if no valid results, return values that indicate failure
            if results is None:
                return float("inf"), "hello"
            
            flights = results.flights

            # save the current query to the supabase
            query_id = self.save_flight_query_to_db(self.departure_airport, self.arrival_airport, self.departure_date, self.num_adults + self.num_children)

            # keep track of the min protected price(later required for unprotected search). So, start with float inf
            min_protected_price = float("inf")

            # keep track of the current rank of each flight option(in the order that Google Flights ranks them)
            curr_rank = 1

            for flight in flights:
                # if flight result is invalid, skip it and continue
                if flight.name == "" or flight.name.strip()[0] == "Self" or flight.departure == "" or flight.arrival == "" or int(flight.price.replace("$", "")) == 0:
                    continue

                # extract the flight price
                flight_price = int(flight.price.replace("$", ""))

                # keep track of the min protected price later when we search for unprotected flights(so we know which unprotected options are reasonable to display)
                min_protected_price = min(min_protected_price, flight_price)

                # extract the number of stops
                num_stops = int(flight.stops)

                # get the duration in minutes
                duration_in_minutes = self.process_time(flight.duration)

                # extract just the departure time(disregard date)
                departure_time = flight.departure.split(" on ")[0]

                # extract just the arrival time(disregard date)
                arrival_time = flight.arrival.split(" on ")[0]

                # represent the airlines in the FlightOption Class as a list
                class_airlines = flight.name.split(", ")

                # represent the airlines in the db as a string(supabase can't store lists)
                db_airlines = flight.name

                # check if this is a multi-airline trip
                if len(class_airlines) > 1:
                    is_multi_airline = True
                else:
                    is_multi_airline = False

                # add FlightOption instance to list of protected search results
                self.protected_flight_results.append(FlightOption(flight_price, num_stops, duration_in_minutes, departure_time, arrival_time, class_airlines, is_multi_airline))
                
                try:
                    self.save_flight_results_to_db(query_id, curr_rank, flight_price, num_stops, duration_in_minutes, departure_time, arrival_time, db_airlines, is_multi_airline)
                except Exception as e:
                    print(f"Connection Error: {e}")
                curr_rank += 1
            
            # get rid of the original representation of flights
            flights = None

            ranked_protected_flight_options = self.rank_flights(self.protected_flight_results, True)

            # return the list of protected flight option results as well as the smallest price for a protected trip
            return ranked_protected_flight_options, min_protected_price
        
        except Exception as e:
            print(e)
            print(f"Couldn't find any valid flight options from {self.departure_airport} to {self.arrival_airport} on {self.departure_date}")
            return float("inf"), "hello"
    

    def search_unprotected_flights(self, min_protected_price):
        major_airports = ["ATL", "FLL", "IAH", "PHX", "BNA", "IAD","PHL", "LGA", "BWI", "MDW", "LAX", "DFW", "DEN", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"] 
        min_unprotected_price = float("inf")
        for airport in major_airports:
            # print(airport)
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

                    # add to self.unprotected_flight_results as (total option, first_leg, second_leg, airport)
                    for second_leg in results.flights:
                        if(int(second_leg.price.replace("$", ""))!=0 and int(second_leg.price.replace("$", "")) + min_first_leg <= min_protected_price + 200):
                            curr_position = 0
                            while(curr_position < len(first_leg_flights) and self.parse_time(second_leg.departure) >= first_leg_flights[curr_position][0] + timedelta(hours = layover_hours)):
                                first_leg = first_leg_flights[curr_position][1]
                                if (int(first_leg.price.replace("$", "")) + int(second_leg.price.replace("$", "")) <= min_protected_price+ 200):
                                    first_leg_price = int(first_leg.price.replace("$", ""))
                                    second_leg_price = int(second_leg.price.replace("$", ""))

                                    first_leg_duration_in_minutes = self.process_time(first_leg.duration)
                                    second_leg_duration_in_minutes = self.process_time(second_leg.duration)

                                    first_leg_departure_time = first_leg.departure.split(" on ")[0]
                                    first_leg_arrival_time = first_leg.arrival.split(" on ")[0]

                                    second_leg_departure_time = second_leg.departure.split(" on ")[0]
                                    second_leg_arrival_time = second_leg.arrival.split(" on ")[0]

                                    first_leg_airlines = [first_leg.name]
                                    second_leg_airlines = [second_leg.name]

                                    if first_leg_airlines == second_leg_airlines:
                                        total_option_airlines = first_leg_airlines
                                    else:
                                        total_option_airlines = [first_leg_airlines[0], second_leg_airlines[0]]
                                    
                                    if len(total_option_airlines) > 1:
                                        total_is_multi_airline = True
                                    else:
                                        total_is_multi_airline = False

                                    min_unprotected_price = min(min_unprotected_price, first_leg_price + second_leg_price)
                                    self.max_unprotected_price = max(self.max_unprotected_price, first_leg_price + second_leg_price)

                                    layover = self.parse_time(second_leg.departure) - self.parse_time(first_leg.arrival)
                                    layover = int(layover.total_seconds() / 60)
                                    self.max_unprotected_duration = max(self.max_unprotected_duration, first_leg_duration_in_minutes + second_leg_duration_in_minutes + layover)

                                    first_leg_option = FlightOption(first_leg_price, 0, first_leg_duration_in_minutes, first_leg_departure_time, first_leg_arrival_time, first_leg_airlines, False)
                                    second_leg_option = FlightOption(second_leg_price, 0, second_leg_duration_in_minutes, second_leg_departure_time, second_leg_arrival_time, second_leg_airlines, False)
                                    total_option = FlightOption(first_leg_price + second_leg_price, 1, first_leg_duration_in_minutes + second_leg_duration_in_minutes + layover, first_leg_departure_time, second_leg_arrival_time, total_option_airlines, total_is_multi_airline)

                                    self.unprotected_flight_results.append((total_option, first_leg_option, second_leg_option, airport))

                                curr_position += 1

                except Exception:
                    continue
        
        ranked_unprotected_flight_results = self.rank_flights(self.unprotected_flight_results, False)
   
        return ranked_unprotected_flight_results, min_unprotected_price
    

    #["ATL", "LAX", "DFW", "DEN", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"] 
    #["SEA", "EWR", "SFO", "PHX", "IAH", "BOS", "FLL", "MSP", "LGA", "DTW", "PHL", "SLC", "BWI", "DCA", "SAN", "IAD", "TPA", "BNA", "AUS", "MDW", "HNL", "DAL", "PDX", "STL", "RDU", "HOU", "OGG", "PIT", "MCI", "MSY", "PHL"]