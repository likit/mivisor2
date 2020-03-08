import os
from collections import defaultdict

from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
from project_dialogs import MainProjectWindow, NewProjectDialog

import sys
import yaml

import pandas as pd

VERSION_NUMBER = '2.0rc'

appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
main_project_window = MainProjectWindow()

class MainWindow(qtw.QMainWindow):
    settings = qtc.QSettings('MUMT', 'Mivisor2')
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Mivisor2')
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        help_menu = menubar.addMenu('Help')
        new_proj_action = file_menu.addAction('New Project...', self.showNewProjectDialog)
        open_action = file_menu.addAction('Open Project', self.openProject)
        open_recent_action = file_menu.addAction('Open Recent Project', lambda: self.openProject(
            self.settings.value('current_proj_dir', '', str)
        ))
        exit_action = file_menu.addAction('Quit', self.close)
        help_action = help_menu.addAction('About', self.showAboutDialog)

        container = qtw.QWidget(self)
        main_layout = qtw.QVBoxLayout(container)
        main_layout.setAlignment(qtc.Qt.AlignCenter)
        title_lbl = qtw.QLabel('<h1>Welcome to Mivisor2</h1>')
        title_lbl.setAlignment(qtc.Qt.AlignHCenter)
        title_lbl.setStyleSheet(
            'QLabel {color: blue}'
        )
        new_proj_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Folder_Add.png'),
            'Create a project', clicked=self.showNewProjectDialog
        )
        open_proj_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Folder.png'),
            'Open a project', clicked=self.openProject
        )
        open_rcnt_proj_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Folder_Upload.png'),
            'Open the recent project',
            clicked=lambda: self.openProject(
                self.settings.value('current_proj_dir', '', str)
            )
        )
        about_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Info.png'),
            'About', clicked=self.showAboutDialog
        )
        exit_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Error.png'),
            'Exit', clicked=self.exitProgram
        )
        new_proj_btn.setStyleSheet(
            'QPushButton {background-color: #fffefa; border: 2px solid white; font-size: 18px}'
        )
        open_proj_btn.setStyleSheet(
            'QPushButton {background-color: #fffefa; border: 2px solid white; font-size: 18px}'
        )
        open_rcnt_proj_btn.setStyleSheet(
            'QPushButton {background-color: #fffefa; border: 2px solid white; font-size: 18px}'
        )
        about_btn.setStyleSheet(
            'QPushButton {background-color: #fffefa; border: 2px solid white; font-size: 18px}'
        )
        exit_btn.setStyleSheet(
            'QPushButton {background-color: #fcebe6; font-size: 18px; border: 1px solid red;}'
        )
        main_layout.addWidget(title_lbl)
        main_layout.addWidget(qtw.QLabel('<h3>Free Software for Microbiology Data Analytics</h3>'))
        version_lbl = qtw.QLabel('<h4>Version {}</h4>'.format(VERSION_NUMBER))
        version_lbl.setAlignment(qtc.Qt.AlignHCenter)
        main_layout.addWidget(version_lbl)
        main_layout.addWidget(new_proj_btn)
        main_layout.addWidget(open_proj_btn)
        main_layout.addWidget(open_rcnt_proj_btn)
        main_layout.addWidget(about_btn)
        main_layout.addWidget(exit_btn)
        self.setCentralWidget(container)

    def showAboutDialog(self):
        about_dialog = qtw.QMessageBox(self)
        about_dialog.setText('About Mivisor2')
        about_dialog.setInformativeText('Mivisor2 is free software for microbiology data analytics.'
                                        '\nThe current version is {}'.format(VERSION_NUMBER))
        about_dialog.setWindowTitle('About')
        about_dialog.setIcon(qtw.QMessageBox.Information)
        about_dialog.setDetailedText('Mivisor2 has been developed by Dr. Preeyanon from'
                                     ' Knowledge and Informatics Lab (KIL)'
                                     ', Faculty of Medical Technology'
                                     ', Mahidol University, Thailand.'
                                     '\n\nThe software is MIT licensed and free for all users WITHOUT WARRANTY OF ANY KIND.'
                                     '\n\nPlease contact likit.pre@mahidol.edu if you have any question or suggestion.')
        about_dialog.setStandardButtons(qtw.QMessageBox.Ok)
        about_dialog.show()

    def showNewProjectDialog(self):
        form = NewProjectDialog(self)
        form.setModal(True)
        form.create_project_signal.connect(self.openProject)
        form.show()


    def exitProgram(self):
        response = qtw.QMessageBox.warning(
            self,
            'Exit Program',
            'Are you sure you want to exit the program?',
            qtw.QMessageBox.Yes|qtw.QMessageBox.No
        )
        if response == qtw.QMessageBox.Yes:
            self.close()

    def openProject(self, project_dir):
        if not project_dir:
            project_dir = qtw.QFileDialog.getExistingDirectory(
                self,
                "Select the project directory...",
                qtc.QDir.homePath(),
            )

        #TODO: insert the current project to the recent project list
        main_project_window.show()
        main_project_window.close_signal.connect(self.show)
        self.close()



if __name__ == '__main__':
    window = MainWindow()
    window.resize(600, 450)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)