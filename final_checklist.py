#final_checklist.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTabWidget, QGroupBox, QTimeEdit, QSpinBox, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTime, pyqtSignal
from PyQt5.QtGui import QIcon
import math


class FinalChecklist(QWidget):
    nextClicked = pyqtSignal()  # Existing signal for next button

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.timeWidgets = {}  # Dictionary to store time widgets
        self.initUI()
        self.setWindowTitle("Final Details")

    def initUI(self):
        self.resize(400, 200)  # Adjust the window size if needed
        self.setWindowIcon(QIcon('daymaker.ico'))
        
        self.mainLayout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        self.mainLayout.addWidget(self.tabWidget)

        # Create a horizontal layout for buttons
        buttonLayout = QHBoxLayout()

        # Next Button
        self.nextButton = QPushButton('Submit', self)
        self.nextButton.clicked.connect(self.onNextClicked)
        buttonLayout.addWidget(self.nextButton)

        # Add the horizontal layout to the main layout
        self.mainLayout.addLayout(buttonLayout)

        # Start and End Time Tab
        self.timeGroup = QGroupBox()
        self.timeLayout = QVBoxLayout()
        self.startTimeEdit = QTimeEdit(self)
        self.endTimeEdit = QTimeEdit(self)
        self.timeLayout.addWidget(QLabel('Start Time:'))
        self.timeLayout.addWidget(self.startTimeEdit)
        self.timeLayout.addWidget(QLabel('End Time:'))
        self.timeLayout.addWidget(self.endTimeEdit)
        self.timeGroup.setLayout(self.timeLayout)
        self.tabWidget.addTab(self.timeGroup, "Start and End Time")

        # Dining Options Tab
        self.diningGroup = QGroupBox()
        self.diningLayout = QVBoxLayout()
        self.diningOptionsInput = QLineEdit(self)
        self.diningLayout.addWidget(QLabel('Dining Options:'))
        self.diningLayout.addWidget(self.diningOptionsInput)
        self.diningGroup.setLayout(self.diningLayout)
        self.tabWidget.addTab(self.diningGroup, "Dining Options")

        # Limitations Tab
        self.limitationsGroup = QGroupBox()
        self.limitationsLayout = QVBoxLayout()
        self.limitationsInput = QTextEdit(self)
        self.limitationsLayout.addWidget(QLabel('Limitations:'))
        self.limitationsLayout.addWidget(self.limitationsInput)
        self.limitationsGroup.setLayout(self.limitationsLayout)
        self.tabWidget.addTab(self.limitationsGroup, "Limitations")

        # Number of Travelers Tab
        self.travelersGroup = QGroupBox()
        self.travelersLayout = QVBoxLayout()
        self.numTravelersSpinBox = QSpinBox(self)
        self.travelersLayout.addWidget(QLabel('Number of Travelers:'))
        self.travelersLayout.addWidget(self.numTravelersSpinBox)
        self.travelersGroup.setLayout(self.travelersLayout)
        self.tabWidget.addTab(self.travelersGroup, "Number of Travelers")

    def onBackClicked(self):
        self.backClicked.emit()

    def onNextClicked(self):
        # Validation checks and data collection here (similar to InitQuestions)
        # Emit the signal if all checks pass
        self.nextClicked.emit()

    def getStartEndTime(self):
        return self.startTimeEdit.time().toString(), self.endTimeEdit.time().toString()

    def createTimeInputs(self):
        # Remove existing widgets in timeLayout
        for i in reversed(range(self.timeLayout.count())): 
            widgetToRemove = self.timeLayout.itemAt(i).widget()
            if widgetToRemove:
                self.timeLayout.removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)

        # Get the total duration in days and additional hours from userInputs
        num_days = self.controller.userInputs.get('duration_days', 0)
        additional_hours = self.controller.userInputs.get('duration_hours', 0)

        # Adjust num_days if there are additional hours
        if additional_hours > 0:
            num_days += 1

        self.timeWidgets.clear()

        for day in range(1, num_days + 1):
            dayLabel = QLabel(f'Day {day}:')
            startTimeEdit = QTimeEdit(self)
            endTimeEdit = QTimeEdit(self)

            start_hour = 9
            defaultStartTime = QTime(start_hour, 0)

            if day < num_days or (day == num_days and additional_hours == 0):
                # Full days (except the last day if there are additional hours)
                defaultEndTime = QTime(18, 0)  # 6 PM
            else:
                # Last day with additional hours
                end_hour = start_hour + additional_hours
                if end_hour >= 24:  # Handle case where end_hour exceeds 24
                    end_hour -= 24
                defaultEndTime = QTime(end_hour, 0)

            startTimeEdit.setTime(defaultStartTime)
            endTimeEdit.setTime(defaultEndTime)

            # Connect the timeChanged signal to the new method
            startTimeEdit.timeChanged.connect(lambda: self.onTimeChanged(startTimeEdit, endTimeEdit))
            endTimeEdit.timeChanged.connect(lambda: self.onTimeChanged(startTimeEdit, endTimeEdit))

            # Store references to the time edits
            self.timeWidgets[day] = (startTimeEdit, endTimeEdit)

            self.timeLayout.addWidget(dayLabel)
            self.timeLayout.addWidget(QLabel('Start Time:'))
            self.timeLayout.addWidget(startTimeEdit)
            self.timeLayout.addWidget(QLabel('End Time:'))
            self.timeLayout.addWidget(endTimeEdit)

    def onTimeChanged(self, startTimeEdit, endTimeEdit):
        """
        Ensures that end time is always after start time.
        If end time is set before start time, both are adjusted to be equal.
        """
        start_time = startTimeEdit.time()
        end_time = endTimeEdit.time()
        if end_time < start_time:
            endTimeEdit.setTime(start_time)

    def getAllDayTimes(self):
        """
        Retrieves start and end times for all days.
        Returns a dictionary with day numbers as keys and tuples of (start time, end time) as values.
        """
        dayTimes = {}
        for day, (startEdit, endEdit) in self.timeWidgets.items():
            dayTimes[day] = (startEdit.time().toString(), endEdit.time().toString())
        return dayTimes

    def getDiningOptions(self):
        return self.diningOptionsInput.text()

    def getLimitations(self):
        return self.limitationsInput.toPlainText()

    def getNumberOfTravelers(self):
        return self.numTravelersSpinBox.value()


