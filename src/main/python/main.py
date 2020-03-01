from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtWidgets as qtw
from new_project_form import NewProjectForm

import sys


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Mivisor2')
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        help_menu = menubar.addMenu('Help')
        new_proj_action = file_menu.addAction('New Project...', self.showNewProjectForm)
        open_action = file_menu.addAction('Open')
        help_action = help_menu.addAction('About', self.showAboutDialog)

        open_icon = self.style().standardIcon(qtw.QStyle.SP_DirOpenIcon)
        open_action.setIcon(open_icon)

    def showAboutDialog(self):
        qtw.QMessageBox.about(
            self,
            "About Mivisor 2",
            "Mivisor 2 is developed by MUMT."
        )

    def showNewProjectForm(self):
        form = NewProjectForm(self)
        form.setModal(True)
        form.show()


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.showMaximized()
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)