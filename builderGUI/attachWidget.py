#*******************************************************************************
#
# $Id: attachWidget.py 52150 2017-03-09 20:36:19Z marissa $
#*******************************************************************************

import os

from tip.qt.pkg import QtCore, QtGui, uic, QtGui

# __dialogs = list()

QtCore.QCoreApplication.setOrganizationName("Tippett")
QtCore.QCoreApplication.setOrganizationDomain("tippett.com")

FILEPATH = os.path.dirname(__file__).replace('builderGUI', 'builderUI')

form_class, base_class = uic.loadUiType(os.path.join(FILEPATH, "attachWidget.ui"))

class AttachWidget(form_class, base_class):

    closeSignal = QtCore.Signal()
    refreshSignal = QtCore.Signal()

    def __init__(self):
        super(AttachWidget, self).__init__()
        self.setupUi(self)
        self.setObjectName('AttachTool')
        self.setWindowTitle('Attach Tool')
        #self.setMinimumSize(250, 600)
        #self.setMaximumSize(250, 600)

        layout = QtGui.QVBoxLayout()
        #layout.addWidget(self.compWidget)
        layout.addWidget(self)
        self.setLayout(layout)

        #self.compWidget.widget_groupBox.toggled.connect(self.showAttach)
        self.attachPoint_groupBox.clicked.connect(self.assignObject)
        self.attachPointNode_groupBox.clicked.connect(self.assignObject)
        self.attachOrient_groupBox.clicked.connect(self.assignObject)
        self.attachOrientNode_groupBox.clicked.connect(self.assignObject)

    def assignObject(self):
        sender = self.sender()

        #checkboxes
        if sender is self.attachPoint_groupBox:
            if self.attachPoint_groupBox.isChecked():
                self.attachPointNode_groupBox.setChecked(False)
        if sender is self.attachPointNode_groupBox:
            if self.attachPointNode_groupBox.isChecked():
                self.attachPoint_groupBox.setChecked(False)

        if sender is self.attachOrient_groupBox:
            if self.attachOrient_groupBox.isChecked():
                self.attachOrientNode_groupBox.setChecked(False)
        if sender is self.attachOrientNode_groupBox:
            if self.attachOrientNode_groupBox.isChecked():
                self.attachOrient_groupBox.setChecked(False)

