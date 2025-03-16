import flightscraper

def main():
    scraper = flightscraper.FlightScraper()
    scraper.askUserForFlightDetails()
    protected_flight_results, min_protected_price = scraper.search_protected_flights()
    print(protected_flight_results)
    scraper.display_recommended_flights(protected_flight_results, True)


    print("Searching unprotected flights")
    unprotected_flight_results, min_unprotected_price = scraper.search_unprotected_flights(min_protected_price)
    print("These are the final flight results:")
    for connecting_airport, first_leg, second_leg in unprotected_flight_results:
        print(f"This is the first leg: {first_leg}")
        print(f"This is the connecting airport {connecting_airport}")
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
# Display top 10 best options(protected by interline agreements) --> remember to check if checked bags/carry-on are allowed. If not, they must be booked.
# and
# Display top 10 best connecting options(not protected by interline agreements) --> min 1.5-2 hours connecting and no checked bags. If checked bags, leave 2-3 hours time. Remember to check if checked bags/carry-on are allowed. If not, they must be booked.
# and 
# If no valid connecting flights exist today, display connecting flights tm
# and
# Display top 10 safest unprotected options(longest layover times possibly even next day)
# and
# Display "SWIVELL's" choice
# and 
# Run Regression on Past Flights to see likelihood of missed connections based on past first leg results
# and
# Display 5 

# Nuances for Unprotected Flights: flights depart from different terminals. Warn them to check airline policies on checked bags/carry ons