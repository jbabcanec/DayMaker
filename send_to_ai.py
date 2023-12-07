# send_to_ai.py

import pandas as pd
import openai
import re

class GPTTurboProcessor:
    def __init__(self, api_key):
        self.file_path = 'userInputs.csv'
        openai.api_key = api_key
        self.hotel_recommendation = None
        self.output_file = 'output.txt'  # File to store the outputs

        # Overwrite or create the output file on each instantiation
        with open(self.output_file, 'w') as f:
            f.write('')  # This will clear the file content or create a new file

    def append_to_file(self, content):
        with open(self.output_file, 'a') as f:
            f.write(content + '\n')

    def initial_hotel_call(self, destination, budget):
        print(f"Making initial call for a hotel in {destination} with a budget level of {budget}.")
        # Adjust the prompt to ask specifically for only the hotel name
        prompt = f"Please provide just the name of a recommended hotel in {destination} for a budget level of {budget} out of 10."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7  # Adjust the temperature as desired for more varied outputs
            )
            # Extracting just the hotel name from the response
            full_response = response['choices'][0]['message']['content']
            # You might need to add additional logic here to ensure only the hotel name is extracted
            self.hotel_recommendation = full_response.split(',')[0].strip()  # Simple extraction by splitting and taking the first part
            print(f"Received hotel recommendation: {self.hotel_recommendation}")
        except openai.error.OpenAIError as e:
            print(f"An error occurred: {e}")

        self.append_to_file(f"Hotel Recommendation: {self.hotel_recommendation}")

        return self.hotel_recommendation

    def process_first_row(self, row, df):
        # Construct the itinerary prompt, specifying that it's for Day 1 only
        prompt_parts = [
            f"Create a very active and detailed itinerary for Day {row['Day']} of a trip to {row['destination']}, strictly between {row['Start Time']} and {row['End Time']} that is very event packed.",
            f"This day is the start of the trip, so begin the itinerary from {row['starting_location']}, make it sequentially sensical",
            f"Include activities that align with these interests: {row['interests']}.",
            f"Plan the day for {row['number_of_travelers']} travelers, considering the limitation: {row['limitations']}.",
            f"Keep the budget at a level {row['budget']} out of 10, with 10 being the most expensive.",
            f"Please put the name of the actual place/store/locations you choose in double quotes."
        ]

        # If hotel is True, specify the itinerary should end with a return to the hotel
        # If hotel is True, specify the itinerary should end with a return to the hotel
        if row['hotel']:
            prompt_parts.append(f"End the night by returning to the hotel {self.hotel_recommendation}, and centralize later activities closer to it.")

        # Check if the first row is not the last row and hotel is False
        if not row.equals(df.iloc[-1]) and not row['hotel']:
            prompt_parts.append("End the day by saying 'Depart for evening sleeping arrangements'.")

        # Check if the current row is both the first and the last row
        if row.equals(df.iloc[0]) and row.equals(df.iloc[-1]):
            prompt_parts.append("End the day by saying 'Depart for home'.")


        # Add dining options based on provided times
        if row['dining_options']:
            breakfast_time = "6-8am" if row['Start Time'] <= "08:00:00" else ""
            lunch_time = "11-1pm" if row['Start Time'] <= "13:00:00" and row['End Time'] >= "11:00:00" else ""
            dinner_time = "5-9pm" if row['End Time'] >= "17:00:00" else ""
            meals = []
            if breakfast_time:
                meals.append("breakfast")
            if lunch_time:
                meals.append("lunch")
            if dinner_time:
                meals.append("dinner")
            if meals:
                prompt_parts.append(f"Include options for {', '.join(meals)} during their respective times.")

        itinerary_prompt = ' '.join(prompt_parts)

        # Make the call to OpenAI's GPT-4 using the chat completions endpoint
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": itinerary_prompt}
                ],
                max_tokens=1000,  # Set a higher max_tokens for a detailed response
                temperature=0.7  # Adjust the temperature as desired for more varied outputs
            )
            # Assume the first message from the model is the itinerary
            itinerary = response['choices'][0]['message']['content'].strip()
            print(f"Day {row['Day']} Itinerary: {itinerary}")
            # Write the itinerary to the file
            self.append_to_file(f"Day {row['Day']} Itinerary:\n{itinerary}")

            # Extract places from the itinerary
            places = re.findall(r'"([^"]+)"', itinerary)

            # Convert the list of places to a set for deduplication
            unique_places = set(places)

            # Write the deduplicated places to a file, excluding the hotel recommendation
            with open("Day1_places.txt", "w") as file:
                for place in unique_places:
                    if place != self.hotel_recommendation:
                        file.write(f"{place}\n")

        except openai.error.OpenAIError as e:
            print(f"An error occurred: {e}")

    def process_middle_rows(self, row):
        # Read previous days' places to avoid repetition
        visited_places = set()
        for day in range(1, row['Day']):
            try:
                with open(f"Day{day}_places.txt", "r") as file:
                    visited_places.update(file.read().splitlines())
            except FileNotFoundError:
                # If a file for a previous day doesn't exist, continue to the next day
                continue

        # Construct the itinerary prompt for the middle day
        prompt_parts = [
            f"Create a very active and detailed itinerary for Day {row['Day']} of a trip to {row['destination']}, strictly between {row['Start Time']} and {row['End Time']} that is very event packed.",
            f"Include activities that align with these interests: {row['interests']}.",
            f"Plan the day for {row['number_of_travelers']} travelers, considering the limitation: {row['limitations']}.",
            f"Keep the budget at a level {row['budget']} out of 10, with 10 being the most expensive.",
            f"Please put the name of the actual place/store/locations you choose in double quotes."
        ]

        if visited_places:
            visited_places_formatted = ', '.join(f'"{place}"' for place in visited_places)
            prompt_parts.append(f"Avoid revisiting these places: {visited_places_formatted}.")

        if row['hotel']:
            prompt_parts.append("Lead first activity by saying 'Depart from the hotel in the morning'.")
        else:
            prompt_parts.append("Lead first activity by saying 'Depart from where you are staying in the morning'.")

        # Ending the day based on the 'hotel' condition
        if row['hotel']:
            prompt_parts.append(f"End the night by returning to the hotel {self.hotel_recommendation}, and centralize later activities closer to it.")
        else:
            prompt_parts.append("End the day by saying 'Depart for evening sleeping arrangements'.")

        # Add dining options based on provided times
        if row['dining_options']:
            breakfast_time = "6-8am" if row['Start Time'] <= "08:00:00" else ""
            lunch_time = "11-1pm" if row['Start Time'] <= "13:00:00" and row['End Time'] >= "11:00:00" else ""
            dinner_time = "5-9pm" if row['End Time'] >= "17:00:00" else ""
            meals = []
            if breakfast_time:
                meals.append("breakfast")
            if lunch_time:
                meals.append("lunch")
            if dinner_time:
                meals.append("dinner")
            if meals:
                prompt_parts.append(f"Include options for {', '.join(meals)} during their respective times.")

        itinerary_prompt = ' '.join(prompt_parts)

        # Make the call to OpenAI's GPT-4 using the chat completions endpoint
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": itinerary_prompt}
                ],
                max_tokens=1000,  # Set a higher max_tokens for a detailed response
                temperature=0.7  # Adjust the temperature as desired for more varied outputs
            )
            # Assume the first message from the model is the itinerary
            itinerary = response['choices'][0]['message']['content'].strip()
            print(f"Day {row['Day']} Itinerary: {itinerary}")
            # Write the itinerary to the file
            self.append_to_file(f"Day {row['Day']} Itinerary:\n{itinerary}")

            # Extract and deduplicate places from the itinerary, excluding the hotel recommendation
            places = set(re.findall(r'"([^"]+)"', itinerary)) - {self.hotel_recommendation}

            # Write the deduplicated places to a file, naming it according to the day
            with open(f"Day{row['Day']}_places.txt", "w") as file:
                for place in places:
                    file.write(f"{place}\n")

        except openai.error.OpenAIError as e:
            print(f"An error occurred: {e}")

    def process_last_row(self, row):
        # Read previous days' places to avoid repetition
        visited_places = set()
        for day in range(1, row['Day']):
            try:
                with open(f"Day{day}_places.txt", "r") as file:
                    visited_places.update(file.read().splitlines())
            except FileNotFoundError:
                continue

        # Construct the itinerary prompt for the last day
        prompt_parts = [
            f"Create a very active and detailed itinerary for Day {row['Day']} of a trip to {row['destination']}, strictly between {row['Start Time']} and {row['End Time']} that is very event packed.",
            f"Include activities that align with these interests: {row['interests']}.",
            f"Plan the day for {row['number_of_travelers']} travelers, considering the limitation: {row['limitations']}.",
            f"Keep the budget at a level {row['budget']} out of 10, with 10 being the most expensive.",
            f"Please put the name of the actual place/store/locations you choose in double quotes."
        ]

        if visited_places:
            visited_places_formatted = ', '.join(f'"{place}"' for place in visited_places)
            prompt_parts.append(f"Avoid revisiting these places: {visited_places_formatted}.")

        if row['hotel']:
            prompt_parts.append("Lead first activity by saying 'Depart from the hotel in the morning'.")
        else:
            prompt_parts.append("Lead first activity by saying 'Depart from where you are staying in the morning'.")

        # Ending the day based on round_trip condition
        if row['round_trip']:
            prompt_parts.append("End with 'End the trip by returning home'.")
        else:
            prompt_parts.append("End with 'End the trip by departing for your next destination city'.")

        # Add dining options based on provided times
        if row['dining_options']:
            breakfast_time = "6-8am" if row['Start Time'] <= "08:00:00" else ""
            lunch_time = "11-1pm" if row['Start Time'] <= "13:00:00" and row['End Time'] >= "11:00:00" else ""
            dinner_time = "5-9pm" if row['End Time'] >= "17:00:00" else ""
            meals = []
            if breakfast_time:
                meals.append("breakfast")
            if lunch_time:
                meals.append("lunch")
            if dinner_time:
                meals.append("dinner")
            if meals:
                prompt_parts.append(f"Include options for {', '.join(meals)} during their respective times.")

        itinerary_prompt = ' '.join(prompt_parts)

        # Make the call to OpenAI's GPT-4 using the chat completions endpoint
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": itinerary_prompt}
                ],
                max_tokens=1000,  # Set a higher max_tokens for a detailed response
                temperature=0.7  # Adjust the temperature as desired for more varied outputs
            )
            # Assume the first message from the model is the itinerary
            itinerary = response['choices'][0]['message']['content'].strip()
            print(f"Day {row['Day']} Itinerary: {itinerary}")
            # Write the itinerary to the file
            self.append_to_file(f"Day {row['Day']} Itinerary:\n{itinerary}")

            # Extract and deduplicate places from the itinerary, excluding the hotel recommendation
            places = set(re.findall(r'"([^"]+)"', itinerary)) - {self.hotel_recommendation}

            # Write the deduplicated places to a file, naming it according to the day
            with open(f"Day{row['Day']}_places.txt", "w") as file:
                for place in places:
                    file.write(f"{place}\n")

        except openai.error.OpenAIError as e:
            print(f"An error occurred: {e}")

    def process_csv(self):
        df = pd.read_csv(self.file_path)
        
        if not df.empty and df.iloc[0]['hotel'] == True:  # Directly compare to the boolean True
            self.initial_hotel_call(df.iloc[0]['destination'], df.iloc[0]['budget'])
        
        if not df.empty:
            print("processing day 1")
            self.process_first_row(df.iloc[0], df)

        if len(df) > 2:
            for _, row in df.iloc[1:-1].iterrows():
                print(f"processing day {row['Day']}")
                self.process_middle_rows(row)
        
        if len(df) > 1:
            print("processing final day")
            self.process_last_row(df.iloc[-1])