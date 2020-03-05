import os

from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import project_dialogs as pjd

import sys
import yaml


class MainWindow(qtw.QMainWindow):
    settings = qtc.QSettings('MUMT', 'Mivisor2')
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Mivisor2')
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        help_menu = menubar.addMenu('Help')
        new_proj_action = file_menu.addAction('New Project...', self.showNewProjectDialog)
        open_action = file_menu.addAction('Open')
        help_action = help_menu.addAction('About', self.showAboutDialog)

        open_icon = qtg.QIcon('../icons/Koloria-Icon-Set/Folder.png')
        open_action.setIcon(open_icon)

        new_proj_icon = qtg.QIcon('../icons/Koloria-Icon-Set/Folder_Add.png')
        new_proj_action.setIcon(new_proj_icon)

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
            qtg.QIcon('../icons/Koloria-Icon-Set/Info_Light.png'),
            'About', clicked=self.showAboutDialog
        )
        exit_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Denided.png'),
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
        main_layout.addWidget(qtw.QLabel(
            '<h3>Free Software for Microbiology Data Analytics</h3>'
        ))
        version_lbl = qtw.QLabel('<h4>Version 2.0</h4>')
        version_lbl.setAlignment(qtc.Qt.AlignHCenter)
        main_layout.addWidget(version_lbl)
        main_layout.addWidget(new_proj_btn)
        main_layout.addWidget(open_proj_btn)
        main_layout.addWidget(open_rcnt_proj_btn)
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
        form = pjd.NewProjectDialog(self)
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
        self.settings.setValue('current_proj_dir', project_dir)

        config_filepath = os.path.join(project_dir, 'config.yml')
        config_data = yaml.load(open(config_filepath, 'r'), Loader=yaml.Loader)
        self.close()
        main_project_window = pjd.MainWindow(self)
        main_project_window.show()
        main_project_window.close_signal.connect(self.show)


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(600, 450)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)