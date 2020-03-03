import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
from config_template import config
import os
import yaml


class NewProjectDialog(qtw.QDialog):
    create_project_signal = qtc.pyqtSignal(str)

    def __init__(self, parent):
        super(NewProjectDialog, self).__init__(parent)

        self.setWindowTitle('Create New Project')

        main_layout = qtw.QVBoxLayout()
        grid_layout = qtw.QGridLayout()
        self.setLayout(main_layout)
        self.project_name_line_edit = qtw.QLineEdit('MyProject')
        self.project_name_line_edit.textChanged.connect(self.updateDirName)
        self.project_dir_line_edit = qtw.QLineEdit()
        self.browse_btn = qtw.QPushButton(clicked=self.openProjDir)
        self.browse_btn.setIcon(self.style().standardIcon(qtw.QStyle.SP_DialogOpenButton))
        self.create_btn = qtw.QPushButton('Create', clicked=self.create)
        self.cancel_btn = qtw.QPushButton('Cancel', clicked=self.destroy)

        grid_layout.addWidget(qtw.QLabel('Project Name'), 0, 0)
        grid_layout.addWidget(self.project_name_line_edit, 0, 1)

        grid_layout.addWidget(qtw.QLabel('Project Directory'), 1, 0)
        grid_layout.addWidget(self.project_dir_line_edit, 1, 1)
        grid_layout.addWidget(self.browse_btn, 1, 2)

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

        self.create_btn.setFocus()

        # Initialize widgets
        self.current_proj_dir = qtc.QDir.homePath()
        self.updateDirName()

        self.resize(600, 100)

    def updateDirName(self):
        projdir = os.path.join(self.current_proj_dir,
                               self.project_name_line_edit.text())
        self.project_dir_line_edit.setText(projdir)

    def openProjDir(self):
        projdir = qtw.QFileDialog.getExistingDirectory(
            self,
            "Select a directory for the project...",
            self.current_proj_dir,
        )
        self.current_proj_dir = projdir
        self.updateDirName()

    def initiate_proj_dir(self, exist=False):
        try:
            if exist:
                os.mkdir(self.project_dir_line_edit.text())

            config_filepath = os.path.join(self.project_dir_line_edit.text(),
                                           self.project_name_line_edit.text() + '.yml')
            config_file = open(config_filepath, 'w')
            yaml.dump(config, stream=config_file, Dumper=yaml.Dumper)
            config_file.close()
        except:
            qtw.QMessageBox.critical(
                self,
                'Error Occurred',
                'Could not create a directory or files.'
            )
            raise
        else:
            qtw.QMessageBox.information(
                self,
                'Project Created',
                'A project has been created.'
            )

    def create(self):
        if not os.path.exists(self.project_dir_line_edit.text()):
            response = qtw.QMessageBox.warning(
                self,
                'Warning',
                'The directory does not exist. Do you want to create it?',
                qtw.QMessageBox.Yes | qtw.QMessageBox.Abort
            )
            if response == qtw.QMessageBox.Yes:
                self.initiate_proj_dir(exist=True)
        else:
            response = qtw.QMessageBox.warning(
                self,
                'Warning',
                'The directory already exists. Some files will be overwritten.',
                qtw.QMessageBox.Yes|qtw.QMessageBox.Abort
            )
            if response == qtw.QMessageBox.Yes:
                self.initiate_proj_dir()
        self.create_project_signal.emit(self.project_dir_line_edit.text())
        self.close()


class MainWindow(qtw.QMainWindow):
    close_signal = qtc.pyqtSignal()
    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)
        main_container = qtw.QWidget()
        vlayout = qtw.QVBoxLayout()
        info_group = qtw.QGroupBox('Information')
        info_group.setLayout(qtw.QVBoxLayout())
        info_group.layout().addWidget(qtw.QLabel('Database File:'))
        info_group.layout().addWidget(qtw.QLabel('Data File:'))
        info_group.setSizePolicy(qtw.QSizePolicy.Preferred,
                                 qtw.QSizePolicy.Fixed)

        field_group = qtw.QGroupBox('Column Properties')
        field_group.setLayout(qtw.QHBoxLayout())

        field_edit_layout = qtw.QVBoxLayout()
        field_edit_layout.addWidget(qtw.QListWidget())
        field_alias_layout = qtw.QHBoxLayout()
        field_alias_edit = qtw.QLineEdit()
        field_alias_edit.setSizePolicy(qtw.QSizePolicy.Preferred,
                                       qtw.QSizePolicy.Fixed)
        field_alias_label = qtw.QLabel('Alias:')
        field_alias_label.setSizePolicy(
            qtw.QSizePolicy.Fixed,
            qtw.QSizePolicy.Fixed
        )
        field_alias_layout.addWidget(field_alias_label)
        field_alias_layout.addWidget(field_alias_edit)
        field_edit_layout.addLayout(field_alias_layout)

        field_type_layout = qtw.QHBoxLayout()
        field_type_layout.setAlignment(qtc.Qt.AlignLeft)
        chk_excluded = qtw.QCheckBox('Excluded')
        chk_key = qtw.QCheckBox('Key')
        chk_drug = qtw.QCheckBox('Drug')
        chk_date = qtw.QCheckBox('Date')
        field_type_layout.addWidget(chk_excluded)
        field_type_layout.addWidget(chk_key)
        field_type_layout.addWidget(chk_drug)
        field_type_layout.addWidget(chk_date)
        field_edit_layout.addLayout(field_type_layout)
        field_group.layout().addLayout(field_edit_layout)
        field_group.layout().addWidget(qtw.QTextEdit())
        field_group.setSizePolicy(qtw.QSizePolicy.Preferred,
                                  qtw.QSizePolicy.Fixed)
        data_table = qtw.QTableView()
        data_table.setSizePolicy(qtw.QSizePolicy.Expanding,
                                 qtw.QSizePolicy.Preferred)
        vlayout.addWidget(info_group)
        vlayout.addWidget(data_table)
        vlayout.addWidget(field_group)
        main_container.setLayout(vlayout)
        self.setCentralWidget(main_container)
        toolbar = self.addToolBar('Data')
        db_connect_action = toolbar.addAction(
            qtg.QIcon('../icons/database/files/48X48/data_right.png'),
            'Connect database',
        )
        db_disconnect_action = toolbar.addAction(
            qtg.QIcon('../icons/database/files/48X48/data_delete.png'),
            'Disconnect database',
        )
        data_import_action = toolbar.addAction(
            # qtg.QIcon('../icons/database/files/48X48/table_add.png'),
            qtg.QIcon('../icons/Koloria-Icon-Set/File_Add.png'),
            'Import data',
        )
        save_config_action = toolbar.addAction(
            qtg.QIcon('../icons/Koloria-Icon-Set/File_List.png'),
            'Save properties',
        )

        db_connect_action.setEnabled(False)
        db_disconnect_action.setEnabled(False)

    def closeEvent(self, event):
        self.close_signal.emit()
