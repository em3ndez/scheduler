# pylint: disable=undefined-variable
import ast
import json
import re
from datetime import datetime, timedelta
from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from constants import WEEK_HOURS, WEEKEND_HOURS
from helpers.excelhelper import ExcelHelper
from helpers.logger import Logger
from helpers.uihelper import UiHelper
from services import scheduler

from .dialog import DialogWindow
from .models import TreeModel
from .ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self._configuration = {}
        self._configPath = ''
        self._requests = {}
        self._holidays = []

        self.setupUi(self)

        self._logger = Logger(self.outputTextEdit)
        self.tabWidget.currentChanged[int].connect(self.updateTabText)
        self.setupConfigurationTab()
        self.setupSchedulerTab()

        self.tabWidget.setCurrentIndex(0)

        self.show()

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        if type(value) is dict:
            self._configuration = value
        else:
            raise TypeError(value)

    @property
    def configPath(self):
        return self._configPath

    @configPath.setter
    def configPath(self, value):
        if value:
            self._configPath = value
            idx = self.tabWidget.currentIndex()
            self.updateTabText(idx)

    def setupConfigurationTab(self):
        # treeview setup
        self.model = TreeModel(None)
        self.treeView.setModel(self.model)

        # action setup
        self.treeView.expanded.connect(self.autoSizeTreeView)

        self.openConfigButton.clicked.connect(self.openConfig)
        self.saveConfigButton.clicked.connect(self.saveConfig)
        self.newConfigButton.clicked.connect(self.newConfig)
        self.newClinicianButton.clicked.connect(self.createNewClinician)
        self.editClinicianButton.clicked.connect(self.editClinician)
        self.deleteClinicianButton.clicked.connect(self.deleteClinician)

        self.newConfig()

    def setupSchedulerTab(self):
        self.loadConfigButton.clicked.connect(self.openConfig)
        self.loadRequestsButton.clicked.connect(self.openRequests)
        self.loadHolidaysButton.clicked.connect(self.openHolidays)
        self.generateScheduleButton.clicked.connect(self.generateSchedule)
        self.exportScheduleButton.clicked.connect(self.exportSchedule)
        self.exportMonthlyButton.clicked.connect(self.exportMonthlySchedule)
        self.exportLpButton.clicked.connect(partial(self.exportLpProblem, mps=False))
        self.exportMpsButton.clicked.connect(partial(self.exportLpProblem, mps=True))

        self.calendarYearSpinBox.setValue(datetime.now().year + 1)

        # misc vars
        self.holidayMap = {}

    def updateTabText(self, selectedTabIdx):
        # clear (configPath) from all other tabs
        for i in range(self.tabWidget.count()):
            text = self.tabWidget.tabText(i)
            newText = re.sub(r'\((?:.*)\)|(\w+)(.*)', r'\1', text)
            self.tabWidget.setTabText(i, newText)

        # leave title as is if there is no config path
        if not self.configPath: return

        text = self.tabWidget.tabText(selectedTabIdx)
        # replace filename in brackets with new config path OR
        # add new config path in brackets, if no brackets yet
        newText = re.sub(r'\((?:.*)\)|(\w+)(.*)', r'\1 ({})'.format(self._configPath), text)
        self.tabWidget.setTabText(selectedTabIdx, newText)

    def autoSizeTreeView(self):
        for i in range(self.model.rootItem.columnCount()):
            self.treeView.resizeColumnToContents(i)

    def openConfig(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open configuration file", "", "JSON files (*.json)"
        )

        if path != '':
            try:
                with open(path, 'r') as f:
                    self.configPath = path
                    self.configuration = json.load(f)
                    UiHelper.syncTreeView(self.treeView, self.model, self.configuration)
                    self._logger.write_line('Loaded configuration file: {}'.format(path))

            except Exception as ex:
                QMessageBox.critical(self, "", "Unable to open file!\nDetails: {}".format(str(ex)))
                self._logger.write_line('Unable to open configuration file. {}'.format(str(ex)), level='ERROR')

    def openRequests(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open requests file", "", "Excel files (*.xlsx *.xlsm)"
        )

        if path != '':
            try:
                self._requests = ExcelHelper.loadRequests(path)
                self._logger.write_line('Loaded requests file: {}'.format(path))

            except Exception as ex:
                QMessageBox.critical(self, "", "Unable to load requests!\nDetails: {}".format(str(ex)))
                self._logger.write_line('Unable to load requests. {}'.format(str(ex)), level='ERROR')

    def openHolidays(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open holidays file", "", "Excel files (*.xlsx *.xlsm)"
        )

        if path != '':
            try:
                self._holidays = ExcelHelper.loadHolidays(path)
                self._logger.write_line('Loaded holidays file: {}'.format(path))

            except Exception as ex:
                QMessageBox.critical(self, "", "Unable to load holidays!\nDetails: {}".format(str(ex)))
                self._logger.write_line('Unable to load holidays. {}'.format(str(ex)), level='ERROR')

    def saveConfig(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "", "JSON files (*.json)"
        )

        if fileName != '':
            try:
                with open(fileName, 'w') as f:
                    data = {}
                    UiHelper.convertTreeToDict(self.model.rootItem, data)
                    json.dump(data, f)
                    self.configPath = fileName
                    self._logger.write_line('Saved configuration file: {}'.format(fileName))

            except Exception as ex:
                QMessageBox.critical(self, "", "Unable to save file!\nDetails: {}".format(str(ex)))

    def newConfig(self):
        # clear data
        self.configuration = {}
        self.configPath = 'new config'
        
        # build treeview
        UiHelper.syncTreeView(self.treeView, self.model, self.configuration)

    def createNewClinician(self):
        dialog = DialogWindow(isEdit=False)
        dialog.setClinicianDictionary(self.configuration)
        dialog.exec_()

        # reset treeview
        UiHelper.syncTreeView(self.treeView, self.model, self.configuration)

    def editClinician(self):
        selectedItem = UiHelper.getSelectedRoot(self.treeView)
        if selectedItem:
            clinData = {}
            UiHelper.convertTreeToDict(selectedItem, clinData)
            clinData["name"] = selectedItem.itemData[0]

            # transfer clinData to edit dialog
            dialog = DialogWindow(isEdit=True)
            dialog.setClinicianDictionary(self.configuration)
            dialog.setClinician(clinData)
            dialog.exec_()

            UiHelper.syncTreeView(self.treeView, self.model, self.configuration)

    def deleteClinician(self):
        selectedItem = UiHelper.getSelectedRoot(self.treeView)
        if selectedItem:
            clinName = selectedItem.itemData[0]
            reply = QMessageBox.question(
                self, 
                "Delete Warning", 
                "This action will delete the current data stored for \"{}\". Are you sure you want to continue?".format(
                    clinName)
                , QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No: return

            del self.configuration[clinName]
            UiHelper.syncTreeView(self.treeView, self.model, self.configuration)

    def setupScheduler(self):
        numClinicians = len(self.configuration.keys())
        if numClinicians <= 0:
            self._logger.write_line('No clinicians configured! Please load a configuration file with at least one clinician!', level='ERROR')
            return

        numBlocks = self.numberOfBlocksSpinBox.value()
        calendarYear = self.calendarYearSpinBox.value()
        constraints = []

        # pull enabled constraints from UI checkboxes
        for row in range(self.constraintsForm.rowCount()):
            widget = self.constraintsForm.itemAt(row, QFormLayout.FieldRole).widget()
            if widget.isChecked():
                constraints.append(widget.objectName().replace('CheckBox', ''))

        return scheduler.Scheduler(
            logger=self._logger, num_blocks=numBlocks, clin_data=self.configuration,
            request_dict=self._requests, holidays=self._holidays,
            constraints=constraints
        )
        
    def exportLpProblem(self, mps=False):
        shuffle = self.shuffleCheckBox.isChecked()

        scheduler = self.setupScheduler()
        if scheduler is None:
            self._logger.write_line('Could not setup scheduler!', level='ERROR')
            return

        scheduler.setup_solver()
        scheduler.setup_problem(shuffle=shuffle)

        problem = scheduler.get_problem()

        if mps:
            dialogName = "Save MPS file"
            dialogExt = "MPS File (*.mps)"
            export = problem.writeMPS
        else:
            dialogName = "Save LP file"
            dialogExt = "LP File (*.lp)"
            export = problem.writeLP

        # choose save location
        path, _ = QFileDialog.getSaveFileName(
            self, dialogName, "", dialogExt, dialogExt
        )

        if path != '':
            try:
                export(path)
                self._logger.write_line('Saved file: {}'.format(path))

            except Exception as ex:
                QMessageBox.critical(self, "", "Unable to save file!\nDetails: {}".format(str(ex)))
                self._logger.write_line('Unable to save file. {}'.format(str(ex)), level='ERROR')


    def generateSchedule(self):
        self.clearScheduleTable()
        shuffle = self.shuffleCheckBox.isChecked()
        verbose = self.verboseCheckBox.isChecked()

        scheduler = self.setupScheduler()
        if scheduler is None:
            self._logger.write_line('Could not setup scheduler!', level='ERROR')
            return

        schedule = scheduler.generate(verbose=verbose, shuffle=shuffle)
        if schedule is None:
            self._logger.write_line('Could not generate schedule! Try adjusting min/max values in the configuration tab.', level='ERROR')
        
        else:
            self._logger.write_line('Generated schedule!')
            divAssignments = schedule[0]
            weekendAssignments = schedule[1]
            self.holidayMap = schedule[2]
            longWeekends = list(self.holidayMap.values())
            
            # create rows for each week num
            for weekNum in range(1, len(weekendAssignments) + 1):
                rowCount = self.scheduleTable.rowCount()
                self.scheduleTable.insertRow(rowCount)
                value = str(weekNum) + '*' if weekNum in longWeekends else str(weekNum)
                self.scheduleTable.setItem(rowCount, 0, QTableWidgetItem(value))

            for divName in divAssignments:
                # create division columns
                assignments = divAssignments[divName]
                columnCount = self.scheduleTable.columnCount()
                self.scheduleTable.insertColumn(columnCount)
                self.scheduleTable.setHorizontalHeaderItem(columnCount, QTableWidgetItem(divName))

                for i in range(len(assignments)):
                    clinName = assignments[i]
                    self.scheduleTable.setItem(i, columnCount, QTableWidgetItem(clinName))

            weekendCol = self.scheduleTable.columnCount()
            self.scheduleTable.insertColumn(weekendCol)
            self.scheduleTable.setHorizontalHeaderItem(weekendCol, QTableWidgetItem("Weekend"))

            for i in range(len(weekendAssignments)):
                clinName = weekendAssignments[i]
                self.scheduleTable.setItem(i, weekendCol, QTableWidgetItem(clinName))               
    
    def exportSchedule(self):
        # open save dialog to let user choose folder + filename
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Excel file", "", "Excel file (*.xlsx)"
        )

        if not fileName: return

        try:
            ExcelHelper.saveYearlySchedule(fileName, self.scheduleTable)
        except IOError as ex:
            QMessageBox.critical(self, "", "Unable to save file!\nDetails: {}".format(str(ex)))

    def exportMonthlySchedule(self):
        # open save dialog to let user choose folder + filename
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Excel file", "", "Excel file (*.xlsx)"
        )

        if not fileName: return

        calendarYear = self.calendarYearSpinBox.value()

        try:
            ExcelHelper.saveMonthlySchedule(fileName, self.scheduleTable, calendarYear, self.holidayMap)
        except IOError as ex:
            QMessageBox.critical(self, "", "Unable to save file!\nDetails: {}".format(str(ex)))

    def clearScheduleTable(self):
        while self.scheduleTable.rowCount() > 0:
            lastRow = self.scheduleTable.rowCount()
            self.scheduleTable.removeRow(lastRow - 1)

        while self.scheduleTable.columnCount() > 1:
            lastColumn = self.scheduleTable.columnCount()
            self.scheduleTable.removeColumn(lastColumn - 1)
