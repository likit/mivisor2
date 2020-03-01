from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from project_dialogs import NewProjectDialog

import sys


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Mivisor2')
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        help_menu = menubar.addMenu('Help')
        new_proj_action = file_menu.addAction('New Project...', self.showNewProjectDialog)
        open_action = file_menu.addAction('Open')
        help_action = help_menu.addAction('About', self.showAboutDialog)

        open_icon = self.style().standardIcon(qtw.QStyle.SP_DirOpenIcon)
        open_action.setIcon(open_icon)

        new_proj_icon = self.style().standardIcon(qtw.QStyle.SP_FileIcon)
        new_proj_action.setIcon(new_proj_icon)

        container = qtw.QWidget(self)
        main_layout = qtw.QVBoxLayout(container)
        main_layout.setAlignment(qtc.Qt.AlignCenter)
        title_lbl = qtw.QLabel('<h1>Welcome to Mivisor2</h1>')
        title_lbl.setAlignment(qtc.Qt.AlignHCenter)
        title_lbl.setStyleSheet(
            'QLabel {color: blue}'
        )
        new_proj_btn = qtw.QPushButton('Create a project', clicked=self.showNewProjectDialog)
        open_proj_btn = qtw.QPushButton('Open a project')
        about_btn = qtw.QPushButton('About', clicked=self.showAboutDialog)
        exit_btn = qtw.QPushButton('Exit', clicked=self.exitProgram)
        new_proj_btn.setStyleSheet(
            'QPushButton {background-color: #fffefa; border: 2px solid white; font-size: 18px}'
        )
        open_proj_btn.setStyleSheet(
            'QPushButton {background-color: #fffefa; border: 2px solid white; font-size: 18px}'
        )
        about_btn.setStyleSheet(
            'QPushButton {background-color: #fffefa; border: 2px solid white; font-size: 18px}'
        )
        exit_btn.setStyleSheet(
            'QPushButton {background-color: #fcebe6; font-size: 18px; border: 1px solid red;}'
        )
        main_layout.addWidget(title_lbl)
        main_layout.addWidget(qtw.QLabel(
            '<h3>Free Software for Microbiology Data Analytics</h3>'
        ))
        version_lbl = qtw.QLabel('<h4>Version 2.0</h4>')
        version_lbl.setAlignment(qtc.Qt.AlignHCenter)
        main_layout.addWidget(version_lbl)
        main_layout.addWidget(new_proj_btn)
        main_layout.addWidget(open_proj_btn)
        main_layout.addWidget(about_btn)
        main_layout.addWidget(exit_btn)
        self.setCentralWidget(container)

    def showAboutDialog(self):
        qtw.QMessageBox.about(
            self,
            "About Mivisor 2",
            "Mivisor 2 is developed by MUMT."
        )

    def showNewProjectDialog(self):
        form = NewProjectDialog(self)
        form.setModal(True)
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


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(600, 450)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)