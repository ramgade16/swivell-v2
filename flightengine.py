import flightscraper

class FlightEngine:

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
        self.checked_bag = input("Will you be flying with a checked bag today? (Answer with an \"Y\" or \"N\") --> ")




def main():
    engine = FlightEngine()
    engine.askUserForFlightDetails()
    
    print("Searching protected flights")
    protected_scraper = flightscraper.FlightScraper(engine.ticket_type, engine.departure_airport, engine.arrival_airport, engine.departure_date, engine.arrival_date, engine.num_adults, engine.num_children, 0)
    direct_flight_results, min_protected_price = protected_scraper.search_flights()
    print("These are the direct flight results:")
    print(direct_flight_results)


    print("Searching unprotected flights")
    unprotected_scraper = flightscraper.FlightScraper(engine.ticket_type, engine.departure_airport, engine.arrival_airport, engine.departure_date, engine.arrival_date, engine.num_adults, engine.num_children, min_protected_price)
    final_flight_results, min_unprotected_price = unprotected_scraper.search_flights()
    print("These are the final flight results:")
    for first_leg, second_leg in final_flight_results:
        print(f"This is the first leg: {first_leg}")
        print(f"This is the second leg: {second_leg}")
        print("")
    
    diff = min_unprotected_price - min_protected_price
    if diff < 0:
        print(f"You can save ${abs(diff)} with SWIVELL's unprotected option!!")
    elif (diff == 0):
        print(f"Both the protected and unprotected trip will cost you ${min_protected_price}. We recommend choosing the protected option. However, you may choose the unprotected option due to preference of airport, layover times, airline, etc.")
    else:
        print(f"The protected trip will save you ${diff}. Therefore, we recommend choosing the protected option.")

if __name__ == "__main__":
    main()


# Goal: 
# Display top 5 best options(protected by interline agreements) --> remember to check if checked bags/carry-on are allowed. If not, they must be booked.
# and
# Display top 5 best connecting options(not protected by interline agreements) --> min 1.5-2 hours connecting and no checked bags. If checked bags, leave 2-3 hours time. Remember to check if checked bags/carry-on are allowed. If not, they must be booked.
# and 
# Display "SWIVELL's" choice