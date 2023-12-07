#init_questions.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QGroupBox, QLabel, QLineEdit, QSpinBox, QCheckBox, QTextEdit, QPushButton, QHBoxLayout, QSlider
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

class InitQuestions(QWidget):
    nextClicked = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initUI()
        self.setWindowTitle("Initial Questions")

    def initUI(self):
        self.resize(300, 200)  # Adjust the window size
        self.setWindowIcon(QIcon('daymaker.ico'))

        mainLayout = QVBoxLayout(self)

        # Create Tab Widget
        tabWidget = QTabWidget(self)

        # Location Panel
        self.locationGroup = QGroupBox()
        locationLayout = QVBoxLayout()
        self.destinationInput = QLineEdit(self)
        locationLayout.addWidget(QLabel('Enter Destination:'))
        locationLayout.addWidget(self.destinationInput)
        self.locationGroup.setLayout(locationLayout)

        # Duration Panel
        self.durationGroup = QGroupBox()
        durationLayout = QVBoxLayout()
        self.daysInput = QSpinBox(self)
        self.hoursInput = QSpinBox(self)
        # self.minutesInput = QSpinBox(self)
        durationLayout.addWidget(QLabel('Days:'))
        durationLayout.addWidget(self.daysInput)
        durationLayout.addWidget(QLabel('Hours:'))
        durationLayout.addWidget(self.hoursInput)
        # durationLayout.addWidget(QLabel('Minutes:'))
        # durationLayout.addWidget(self.minutesInput)
        self.suggestHotelsCheckbox = QCheckBox("Suggest Hotels", self)
        self.suggestHotelsCheckbox.setEnabled(False)
        self.daysInput.valueChanged.connect(self.checkDays)
        durationLayout.addWidget(self.suggestHotelsCheckbox)
        self.durationGroup.setLayout(durationLayout)

        # Budget Panel
        self.budgetGroup = QGroupBox()
        budgetLayout = QVBoxLayout()
        budgetSliderLayout = QHBoxLayout()
        budgetSliderLayout.addWidget(QLabel('$'))
        self.budgetSlider = QSlider(Qt.Horizontal, self)
        self.budgetSlider.setMinimum(1)
        self.budgetSlider.setMaximum(10)
        self.budgetSlider.setTickPosition(QSlider.TicksBelow)
        self.budgetSlider.setTickInterval(1)
        budgetSliderLayout.addWidget(self.budgetSlider)
        budgetSliderLayout.addWidget(QLabel('$$$$'))
        budgetLayout.addLayout(budgetSliderLayout)
        self.budgetGroup.setLayout(budgetLayout)

        # Interests Panel
        self.interestsGroup = QGroupBox()
        interestsLayout = QVBoxLayout()
        self.interestsInput = QTextEdit(self)
        interestsLayout.addWidget(QLabel('Enter Interests:'))
        interestsLayout.addWidget(self.interestsInput)
        self.interestsGroup.setLayout(interestsLayout)

        # Add tabs to the tab widget
        tabWidget.addTab(self.locationGroup, "Location")
        tabWidget.addTab(self.durationGroup, "Duration")
        tabWidget.addTab(self.budgetGroup, "Budget")
        tabWidget.addTab(self.interestsGroup, "Interests")

        # Add Tab Widget to the main layout
        mainLayout.addWidget(tabWidget)

        # Next Button
        self.nextButton = QPushButton('Next', self)
        self.nextButton.clicked.connect(self.onNextClicked)
        mainLayout.addWidget(self.nextButton)

    def onNextClicked(self):
        # Validation checks
        if not self.destinationInput.text().strip():
            QMessageBox.warning(self, 'Validation Error', 'Please enter a destination.')
            return

        if self.daysInput.value() == 0 and self.hoursInput.value() == 0 and self.minutesInput.value() == 0:
            QMessageBox.warning(self, 'Validation Error', 'Please enter a valid duration.')
            return

        if not self.interestsInput.toPlainText().strip():
            QMessageBox.warning(self, 'Validation Error', 'Please enter your interests.')
            return

        #If all checks pass, emit the signal
        self.nextClicked.emit()

    def checkDays(self):
        # Enable checkbox only if days > 0
        self.suggestHotelsCheckbox.setEnabled(self.daysInput.value() > 0)

    def isHotel(self):
        return self.suggestHotelsCheckbox.isChecked()
