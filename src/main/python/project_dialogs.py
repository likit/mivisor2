import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import os


class NewProjectForm(qtw.QDialog):
    def __init__(self, parent):
        super(NewProjectForm, self).__init__(parent)

        self.setWindowTitle('Create New Project')

        main_layout = qtw.QVBoxLayout()
        grid_layout = qtw.QGridLayout()
        self.setLayout(main_layout)
        self.project_name_line_edit = qtw.QLineEdit('MyProject')
        self.project_name_line_edit.textChanged.connect(self.updateDirName)
        self.project_dir_line_edit = qtw.QLineEdit()
        self.project_db_line_edit = qtw.QLineEdit()
        self.browse_btn = qtw.QPushButton()
        self.browse_db_btn = qtw.QPushButton()
        self.browse_btn.setIcon(self.style().standardIcon(qtw.QStyle.SP_DialogOpenButton))
        self.browse_db_btn.setIcon(self.style().standardIcon(qtw.QStyle.SP_DialogOpenButton))
        self.create_btn = qtw.QPushButton('Create')
        self.cancel_btn = qtw.QPushButton('Cancel', clicked=self.destroy)

        grid_layout.addWidget(qtw.QLabel('Project Name'), 0, 0)
        grid_layout.addWidget(self.project_name_line_edit, 0, 1)

        grid_layout.addWidget(qtw.QLabel('Project Directory'), 1, 0)
        grid_layout.addWidget(self.project_dir_line_edit, 1, 1)
        grid_layout.addWidget(self.browse_btn, 1, 2)

        grid_layout.addWidget(qtw.QLabel('Project Database'), 2, 0)
        grid_layout.addWidget(self.project_db_line_edit, 2, 1)
        grid_layout.addWidget(self.browse_db_btn, 2, 2)

        button_layout = qtw.QHBoxLayout()
        button_layout.setAlignment(qtc.Qt.AlignCenter)
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.cancel_btn)
        self.create_btn.setSizePolicy(qtw.QSizePolicy.Fixed,
                                      qtw.QSizePolicy.Fixed)
        self.cancel_btn.setSizePolicy(qtw.QSizePolicy.Fixed,
                                      qtw.QSizePolicy.Fixed)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(button_layout)

        self.updateDirName()  # initiate the directory
        self.create_btn.setFocus()
        self.resize(600, 200)

    def updateDirName(self):
        projdir = os.path.join(os.getcwd(), self.project_name_line_edit.text())
        dbdir = os.path.join(projdir, 'main.db')
        self.project_dir_line_edit.setText(projdir)
        self.project_db_line_edit.setText(dbdir)
