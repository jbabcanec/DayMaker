# DayMaker - The Itinerary Builder

## Description

This is an itinerary builder which makes use of the GPT-4 API. It will return an `output.txt` file that describes a detailed hour-by-hour itinerary of your choosing.

## Installation

To install the necessary libraries, download the `requirements.txt` file and run the following command in your terminal or command prompt:

\```bash
pip install -r requirements.txt
\```

This will install all the required packages for the project.

## Usage

Fill out all constituent tabs of each panel. Make sure not to use too many days as this will take a while. The hour planner on the final panel will reflect the amount of time used on a day and overwrite any remaining amount of hour chosen. This system is robust, so no need to worry about spelling, but please do use full names of cities with state.

## Credentials

You need to obtain an OpenAI API key and put it in a `credentials.txt` file in the project's root directory. No quotes are necessary; just the key will do on the first line.

## License

This software is provided "as is", without warranty of any kind, express or implied. No rights are granted for redistribution or commercial use without explicit permission from the author. All other rights reserved.

For inquiries or permission requests, please contact joseph.babz@gmail.com.
