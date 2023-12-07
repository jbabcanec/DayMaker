#gps_panel.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from PyQt5.QtCore import pyqtSignal
import requests
from PyQt5.QtGui import QIcon

class GPSPanel(QWidget):
    nextClicked = pyqtSignal()  # Define the signal

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initUI()
        self.setWindowTitle("GPS Panel")

    def initUI(self):
        self.resize(300, 150)  # Adjust the window size
        self.setWindowIcon(QIcon('daymaker.ico'))
        mainLayout = QVBoxLayout(self)

        # Starting Location Input
        self.startingLocationInput = QLineEdit(self)
        mainLayout.addWidget(QLabel('Starting Location:'))
        mainLayout.addWidget(self.startingLocationInput)

        # 'Use My Location' Button
        self.useMyLocationButton = QPushButton('Use My Location', self)
        self.useMyLocationButton.clicked.connect(self.onUseMyLocation)
        mainLayout.addWidget(self.useMyLocationButton)

        # Round Trip Checkbox
        self.roundTripCheckbox = QCheckBox('Round Trip', self)
        mainLayout.addWidget(self.roundTripCheckbox)

        # Next Button
        self.nextButton = QPushButton('Next', self)
        self.nextButton.clicked.connect(self.onNextClicked)
        mainLayout.addWidget(self.nextButton)

    def onUseMyLocation(self):
        try:
            response = requests.get('http://ip-api.com/json/')
            if response.status_code == 200:
                data = response.json()
                city = data['city']
                state = data['regionName']
                country = data['country']
                location = f"{city}, {state}, {country}"
                self.startingLocationInput.setText(location)
            else:
                QMessageBox.warning(self, 'Error', 'Unable to fetch location')
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))

    def onNextClicked(self):
        # Validation check for Starting Location
        if not self.startingLocationInput.text().strip():
            QMessageBox.warning(self, 'Validation Error', 'Please enter a starting location or use "Use My Location".')
            return

        # If the check passes, emit the signal
        self.nextClicked.emit()

    # Additional methods to get data from this panel
    def getStartingLocation(self):
        return self.startingLocationInput.text()

    def isRoundTrip(self):
        return self.roundTripCheckbox.isChecked()