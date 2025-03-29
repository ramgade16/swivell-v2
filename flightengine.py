import flightscraper

def main():
    scraper = flightscraper.FlightScraper()
    scraper.askUserForFlightDetails()
    protected_flight_results, min_protected_price = scraper.search_protected_flights()

    print("These are the 10 best Protected Flight Results:")

    for curr_option in range(min(10, len(protected_flight_results))):
        print(f"Option {curr_option + 1}:")
        curr_flight = protected_flight_results[curr_option]
        duration_hours = int(curr_flight.duration_in_minutes/60)
        duration_minutes = curr_flight.duration_in_minutes % 60
        print(f"[(Airlines: {curr_flight.airlines}), (Departure Airport: {scraper.departure_airport}), (Arrival Airport: {scraper.arrival_airport}), (Departure Time: {curr_flight.departure_time}), (Arrival Time: {curr_flight.arrival_time}), (Duration: {duration_hours} hrs {duration_minutes} mins), (Price: {curr_flight.price})]")
        print("")




    print("")
    print("")
    unprotected_flight_results, min_unprotected_price = scraper.search_unprotected_flights(min_protected_price)

    if len(unprotected_flight_results) == 0:
        print("There are no reasonable Unprotected Flight Results.")
        print("")
    else:
        print("These are the 10 best Unprotected Flight Results:")
        curr_option = 1
        for total_option, first_leg_option, second_leg_option, layover_airport in unprotected_flight_results:
            if curr_option == 21:
                break
            print(f"Option {int(curr_option/2) + 1}:")
            print("Total Option:")
            total_option_duration_hours = int(total_option.duration_in_minutes/60)
            total_option_duration_minutes = total_option.duration_in_minutes % 60
            print(f"[(Airlines: {total_option.airlines}), (Departure Airport: {scraper.departure_airport}), (Layover Airport: {layover_airport}), (Arrival Airport: {scraper.arrival_airport}), (Departure Time: {total_option.departure_time}), (Arrival Time: {total_option.arrival_time}), (Duration: {total_option_duration_hours} hrs {total_option_duration_minutes} mins), (Price: {total_option.price})]")
            print("Leg 1:")
            first_leg_duration_hours = int(first_leg_option.duration_in_minutes/60)
            first_leg_duration_minutes = first_leg_option.duration_in_minutes % 60
            print(f"[(Airlines: {first_leg_option.airlines}), (Departure Airport: {scraper.departure_airport}), (Arrival Airport: {layover_airport}), (Departure Time: {first_leg_option.departure_time}), (Arrival Time: {first_leg_option.arrival_time}), (Duration: {first_leg_duration_hours} hrs {first_leg_duration_minutes} mins)]")
            print("Leg 2:")
            second_leg_duration_hours = int(second_leg_option.duration_in_minutes/60)
            second_leg_duration_minutes = second_leg_option.duration_in_minutes % 60
            print(f"[(Airlines: {second_leg_option.airlines}), (Departure Airport: {layover_airport}), (Arrival Airport: {scraper.arrival_airport}), (Departure Time: {second_leg_option.departure_time}), (Arrival Time: {second_leg_option.arrival_time}), (Duration: {second_leg_duration_hours} hrs {second_leg_duration_minutes} mins)]")
            print("")
            curr_option += 2
    

    diff = min_unprotected_price - min_protected_price
    if len(unprotected_flight_results) == 0:
        print("Please choose one of the Protected Flight Results!")
    elif diff < 0:
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
# Display top 10 safest unprotected options(longest layover times possibly even next day)
# and
# Display "SWIVELL's" choice
# and 
# Run Regression on Past Flights to see likelihood of missed connections based on past first leg results
# and
# Offer a dashboard that compares options side-by-side, highlighting key differences with AI-generated insights.
# and
# Flight Recommendation AI Model (Ranking Engine):

# Implement a Machine Learning model (Regression/Neural Network) to predict the best flight options based on:

# Historical flight data (prices, delays, missed connections).

# User preferences (cost, duration, layover time, airline preference, etc.).

# Risk evaluation for unprotected flights (likelihood of missing connections based on past data).

# Use AI to rank and recommend flights dynamically based on the user's preferences.

# Nuances for Unprotected Flights: flights depart from different terminals. Warn them to check airline policies on checked bags/carry ons

# REFINE DISPLAY ALGORITHM TO DISPLAY BEST FLIGHTS

# If no valid connecting flights exist today, display connecting flights tm
# and
#Implement Redirection to Expedia (much more predictable)