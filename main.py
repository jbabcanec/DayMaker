#main.py

import csv
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

from init_questions import InitQuestions
from gps_panel import GPSPanel
from final_checklist import FinalChecklist 
from send_to_ai import GPTTurboProcessor

class MainController:
    def __init__(self, app):
        self.app = app

        # Read the API key from credentials.txt
        with open('credentials.txt', 'r') as file:
            api_key = file.read().strip()

        self.gpt_processor = GPTTurboProcessor(api_key)  # API key is read from credentials.txt

        # Initialize userInputs before creating other instances
        self.userInputs = {}

        self.init_questions = InitQuestions(self)
        self.gps_panel = GPSPanel(self)
        self.final_checklist = FinalChecklist(self)  # Create an instance of FinalChecklist

        # Connect signals to handlers
        self.init_questions.nextClicked.connect(self.collectDataAndShowGPSPanel)
        self.gps_panel.nextClicked.connect(self.collectDataAndShowFinalChecklist)
        self.final_checklist.nextClicked.connect(self.finishOrNextPanel)  # Assuming you have another panel or a finish method

        # Variables to store user inputs
        self.userInputs = {}

    def start(self):
        self.init_questions.show()

    def collectDataAndShowGPSPanel(self):
        # Collect data from InitQuestions
        self.collectDataFromInitQuestions()

        # Transition to GPSPanel
        self.init_questions.close()
        self.gps_panel.show()

    def collectDataAndShowFinalChecklist(self):
        # Collect data from GPSPanel
        self.collectDataFromGPSPanel()

        # Update the time inputs in FinalChecklist based on the number of days
        self.final_checklist.createTimeInputs()

        # Transition to FinalChecklist
        self.gps_panel.close()
        self.final_checklist.show()

    def collectDataFromInitQuestions(self):
        # Collect data from InitQuestions
        self.userInputs['destination'] = self.init_questions.destinationInput.text()
        self.userInputs['duration_days'] = self.init_questions.daysInput.value()
        self.userInputs['duration_hours'] = self.init_questions.hoursInput.value()
        self.userInputs['hotel'] = self.init_questions.isHotel()
        # self.userInputs['duration_minutes'] = self.init_questions.minutesInput.value()
        self.userInputs['budget'] = self.init_questions.budgetSlider.value()
        self.userInputs['interests'] = self.init_questions.interestsInput.toPlainText()

    def collectDataFromGPSPanel(self):
        # Collect data from GPSPanel
        self.userInputs['starting_location'] = self.gps_panel.getStartingLocation()
        self.userInputs['round_trip'] = self.gps_panel.isRoundTrip()

    def collectDataFromFinalChecklist(self):
        # Collect general data from FinalChecklist
        self.userInputs['dining_options'] = self.final_checklist.getDiningOptions()
        self.userInputs['limitations'] = self.final_checklist.getLimitations()
        self.userInputs['number_of_travelers'] = self.final_checklist.getNumberOfTravelers()

        # Collect start and end times for each day
        allDayTimes = self.final_checklist.getAllDayTimes()
        self.userInputs['day_times'] = allDayTimes

    def finishOrNextPanel(self):
        # Collect data from FinalChecklist
        self.collectDataFromFinalChecklist()

        # Export data to a CSV file
        self.exportDataToCSV()

        # Process the exported CSV file with GPTTurboProcessor
        self.gpt_processor.file_path = "userInputs.csv"  # Update the file_path attribute with the CSV file name
        self.gpt_processor.process_csv()  # Process the CSV to generate itineraries

        # Display a message box to the user
        msg = QMessageBox()
        msg.setWindowTitle("Itinerary Generated")
        msg.setText("Itinerary generated. Enjoy!")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.exitApplication)  # Connect the button click to an exit function
        msg.exec_()  # Display the message box

    def exportDataToCSV(self):
        # Define the CSV file name
        filename = "userInputs.csv"

        # Open the file and write the data
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Prepare the header
            header = list(self.userInputs.keys())
            header.remove('day_times')  # Remove 'day_times' from the header
            header.extend(['Day', 'Start Time', 'End Time'])  # Add day-specific headers
            writer.writerow(header)

            # Iterate over each day and write data
            for day, times in self.userInputs['day_times'].items():
                row = [self.userInputs.get(key) for key in self.userInputs if key != 'day_times']
                row.extend([day, times[0], times[1]])  # Append day-specific data
                writer.writerow(row)

        print(f"Data exported to {filename}")

    def exitApplication(self):
        self.app.quit()  # Close the application



if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = MainController(app)
    controller.start()
    sys.exit(app.exec_())