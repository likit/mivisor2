import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import xlrd
import pandas as pd

from config_template import config
import os
import yaml


class NotificationDialog(qtw.QDialog):
    def __init__(self, parent, title, message):
        super(NotificationDialog, self).__init__(parent=parent)
        layout = qtw.QHBoxLayout()
        layout.setAlignment(qtc.Qt.AlignHCenter)
        layout.addWidget(qtw.QLabel(message))
        self.setWindowTitle(title)
        self.setLayout(layout)


class XlrdOpenFileThread(qtc.QThread):
    xlrd_read_workbook_error = qtc.pyqtSignal(Exception)
    xlrd_read_workbook_finished = qtc.pyqtSignal(list)

    def __init__(self, filename):
        super(XlrdOpenFileThread, self).__init__()
        self.filename = filename

    def run(self):
        try:
            worksheets = xlrd.open_workbook(self.filename).sheet_names()
        except Exception as e:
            self.xlrd_read_workbook_error.emit(e)
        else:
            self.xlrd_read_workbook_finished.emit(worksheets)


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

            config_filepath = os.path.join(self.project_dir_line_edit.text(), 'config.yml')
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
    settings = qtc.QSettings('MUMT', 'Mivisor2')

    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)
        self.config_data = None

        main_container = qtw.QWidget()
        vlayout = qtw.QVBoxLayout()
        info_group = qtw.QGroupBox('Information')
        info_group.setLayout(qtw.QVBoxLayout())
        info_group.layout().addWidget(
            qtw.QLabel(
                'Project directory: {}'.format(
                    self.settings.value('current_proj_dir', '', type=str)
                )
            )
        )

        self.creator_label = qtw.QLabel()
        info_group.layout().addWidget(self.creator_label)
        info_group.layout().addWidget(qtw.QLabel('Current Database: '))
        info_group.setSizePolicy(qtw.QSizePolicy.Preferred,
                                 qtw.QSizePolicy.Fixed)
        self.load_config()

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
            self.openImportDialog
        )

        save_config_action = toolbar.addAction(
            qtg.QIcon('../icons/Koloria-Icon-Set/File_List.png'),
            'Save properties',
        )

        project_config_action = toolbar.addAction(
            qtg.QIcon('../icons/Koloria-Icon-Set/Gear.png'),
            'Project Settings',
            self.openConfigDialog
        )

        close_proj_action = toolbar.addAction(
            qtg.QIcon('../icons/Koloria-Icon-Set/Error.png'),
            'Close project',
            self.close
        )

        help_action = toolbar.addAction(
            qtg.QIcon('../icons/Koloria-Icon-Set/Help.png'),
            'Help',
        )

        db_connect_action.setEnabled(False)
        db_disconnect_action.setEnabled(False)

    def load_config(self):
        config_filepath = os.path.join(self.settings.value('current_proj_dir', '', str), 'config.yml')
        if config_filepath and os.path.exists(config_filepath):
            self.config_data = yaml.load(open(config_filepath, 'r'), Loader=yaml.Loader)
            self.creator_label.setText('Creator: {}'.format(self.config_data.get('creator')))
        else:
            qtw.QMessageBox(
                self,
                'Config file not found.',
                'The config file is missing. Cannot proceed.',
                qtw.QMessageBox.Ok
            )
            self.close()

    def openConfigDialog(self):
        project_setting_dialog = ProjectSettingDialog(self, self.config_data)
        project_setting_dialog.update_config_signal.connect(self.load_config)

    def closeEvent(self, event):
        self.close_signal.emit()

    def openImportDialog(self):
        projdir = self.settings.value('current_proj_dir')
        print(projdir)
        if not projdir:
            projdir = qtc.QDir.homePath()

        filename, type_ = qtw.QFileDialog.getOpenFileName(
            self,
            'Import Excel file',
            projdir,
            "Excel files (*.xls *.xlsx)"
        )
        if filename:
            self.xlrd_reader = XlrdOpenFileThread(filename)
            self.xlrd_reader.xlrd_read_workbook_finished.connect(self.showWorksheetListDlg)
            self.xlrd_reader.xlrd_read_workbook_error.connect(
                lambda e: qtw.QMessageBox.critical(
                    self,
                    'Error Occurred',
                    str(e)
                )
            )
            self.xlrd_reader.started.connect(self.openXlrdDlg)
            self.xlrd_reader.start()

    def openXlrdDlg(self):
        self.xlrd_dlg = NotificationDialog(self,
                                           'Information',
                                           'Reading from the Excel file, please wait..')
        self.xlrd_dlg.setModal(True)
        self.xlrd_dlg.show()

    #TODO: use a better method name
    def showWorksheetListDlg(self, worksheets):
        self.xlrd_dlg.close()
        worksheet, ok = qtw.QInputDialog.getItem(
            self,
            'Select a worksheet',
            'Worksheets',
            worksheets,
            0,
            False
        )



class ProjectSettingDialog(qtw.QDialog):
    settings = qtc.QSettings('MUMT', 'Mivisor2')
    update_config_signal = qtc.pyqtSignal(bool)

    def __init__(self, parent, config_data):
        super(ProjectSettingDialog, self).__init__(parent, modal=True)
        layout = qtw.QVBoxLayout()
        self.config_data = config_data
        self.setWindowTitle('Project Settings')
        self.setLayout(layout)

        self.creator_edit = qtw.QLineEdit(self.config_data.get('creator', 'Unknown'))
        self.desc_edit = qtw.QTextEdit(self.config_data.get('desc', ''))
        form_layout = qtw.QFormLayout()
        form_layout.addRow('Creator', self.creator_edit)
        form_layout.addRow('Description', self.desc_edit)
        button_box = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Save|qtw.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.resize(400, 200)
        self.show()

    def accept(self):
        config_filepath = os.path.join(self.settings.value('current_proj_dir'), 'config.yml')
        if self.creator_edit.text():
            self.config_data['creator'] = self.creator_edit.text()
        self.config_data['desc'] = self.desc_edit.toPlainText()
        yaml.dump(self.config_data,
                  stream=open(config_filepath, 'w'),
                  Dumper=yaml.Dumper)
        self.update_config_signal.emit(True)
        super(ProjectSettingDialog, self).accept()

    def reject(self):
        super(ProjectSettingDialog, self).reject()

