# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src\designer\dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(522, 357)
        Dialog.setModal(True)
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setGeometry(QtCore.QRect(3, 8, 511, 341))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.layoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(self.layoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.emailLabel = QtWidgets.QLabel(self.layoutWidget)
        self.emailLabel.setObjectName("emailLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.emailLabel)
        self.emailLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.emailLineEdit.setObjectName("emailLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.emailLineEdit)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.divisionTable = QtWidgets.QTableWidget(self.layoutWidget1)
        self.divisionTable.setObjectName("divisionTable")
        self.divisionTable.setColumnCount(3)
        self.divisionTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.divisionTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.divisionTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.divisionTable.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.divisionTable)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addButton = QtWidgets.QToolButton(self.layoutWidget1)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout.addWidget(self.addButton)
        self.removeButton = QtWidgets.QToolButton(self.layoutWidget1)
        self.removeButton.setObjectName("removeButton")
        self.horizontalLayout.addWidget(self.removeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dialogButtonBox = QtWidgets.QDialogButtonBox(self.splitter)
        self.dialogButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.dialogButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.dialogButtonBox.setObjectName("dialogButtonBox")
        self.actionAddDivision = QtWidgets.QAction(Dialog)
        self.actionAddDivision.setObjectName("actionAddDivision")
        self.actionRemoveDivision = QtWidgets.QAction(Dialog)
        self.actionRemoveDivision.setObjectName("actionRemoveDivision")

        self.retranslateUi(Dialog)
        self.dialogButtonBox.accepted.connect(Dialog.accept)
        self.dialogButtonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Clinician Details"))
        self.nameLabel.setText(_translate("Dialog", "Name"))
        self.emailLabel.setText(_translate("Dialog", "Email"))
        item = self.divisionTable.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Division Name"))
        item = self.divisionTable.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Minimum Blocks"))
        item = self.divisionTable.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Maximum Blocks"))
        self.addButton.setToolTip(_translate("Dialog", "<html><head/><body><p>Add a new division...</p></body></html>"))
        self.addButton.setText(_translate("Dialog", "Add"))
        self.removeButton.setToolTip(_translate("Dialog", "<html><head/><body><p>Remove selected division...</p></body></html>"))
        self.removeButton.setText(_translate("Dialog", "Remove"))
        self.actionAddDivision.setText(_translate("Dialog", "Add"))
        self.actionAddDivision.setToolTip(_translate("Dialog", "Add new division..."))
        self.actionRemoveDivision.setText(_translate("Dialog", "Remove"))
        self.actionRemoveDivision.setToolTip(_translate("Dialog", "Remove selected division..."))
        self.actionRemoveDivision.setShortcut(_translate("Dialog", "Del"))

