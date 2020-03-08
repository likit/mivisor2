import os
from collections import defaultdict

import xlrd
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
import datetime as dt
import yaml

import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg

from data_models import PandasModel
from config_template import config


class NotificationDialog(qtw.QDialog):
    def __init__(self, parent, title, message, modal=True):
        super(NotificationDialog, self).__init__(parent=parent)
        layout = qtw.QHBoxLayout()
        layout.setAlignment(qtc.Qt.AlignHCenter)
        layout.addWidget(qtw.QLabel(message))
        self.setWindowTitle(title)
        self.setLayout(layout)
        self.setModal(modal)
        self.show()


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


class PandasReadExcelThread(qtc.QThread):
    pandas_read_excel_finished = qtc.pyqtSignal(pd.DataFrame)
    pandas_read_excel_error = qtc.pyqtSignal(Exception)

    def __init__(self, filename, sheet):
        super(PandasReadExcelThread, self).__init__()
        self.filename = filename
        self.sheet = sheet

    def run(self):
        try:
            df = pd.read_excel(self.filename, self.sheet)
        except Exception as e:
            self.pandas_read_excel_error.emit(e)
        else:
            self.pandas_read_excel_finished.emit(df)


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
                qtw.QMessageBox.Yes | qtw.QMessageBox.Abort
            )
            if response == qtw.QMessageBox.Yes:
                self.initiate_proj_dir()
        self.create_project_signal.emit(self.project_dir_line_edit.text())
        self.close()


class MainProjectWindow(qtw.QMainWindow):
    close_signal = qtc.pyqtSignal()
    settings = qtc.QSettings('MUMT', 'Mivisor2')

    def __init__(self):
        super(MainProjectWindow, self).__init__()
        self.config_data = None

        menubar = self.menuBar()
        project_menu = menubar.addMenu('Project')
        project_close = project_menu.addAction('Close', self.close)
        registry_menu = menubar.addMenu('Registry')
        tool_menu = menubar.addMenu('Tools')
        group_value_menu = tool_menu.addMenu('Group values')
        self.group_text_menu = group_value_menu.addAction('Group text values', self.showGroupValuesDialog)
        self.manage_groups = group_value_menu.addAction('Manage columns')
        drug_registry = registry_menu.addAction('Drug', self.showDrugRegistryDialog)
        organism_registry = registry_menu.addAction('Organism', self.showOrgRegistryDialog)

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
        self.column_treewidget = qtw.QTreeWidget()
        self.column_treewidget.setHeaderLabels(['Name', 'Key', 'Date', 'Drug', 'Organism', 'Alias', 'Description'])
        self.column_treewidget.setAlternatingRowColors(True)
        self.column_treewidget.itemClicked.connect(self.column_treewidget_item_clicked)
        self.column_treewidget.currentItemChanged.connect(self.column_treewidget_current_item_changed)
        self.column_treewidget.setSelectionMode(qtw.QAbstractItemView.SingleSelection)
        field_edit_layout.addWidget(self.column_treewidget)

        field_group.layout().addLayout(field_edit_layout)
        self.info_textedit = qtw.QTextEdit()
        field_group.layout().addWidget(self.info_textedit)
        field_group.setSizePolicy(qtw.QSizePolicy.Preferred,
                                  qtw.QSizePolicy.Fixed)
        self.data_table = qtw.QTableView()
        self.data_table.setSizePolicy(qtw.QSizePolicy.Expanding,
                                      qtw.QSizePolicy.Preferred)
        self.data_table.setSelectionBehavior(qtw.QTableView.SelectColumns)
        self.data_table.clicked.connect(self.data_table_item_changed)
        self.data_table.horizontalHeader().sectionClicked.connect(self.data_table_column_changed)
        vlayout.addWidget(info_group)
        vlayout.addWidget(self.data_table)
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
            'Save profile',
            self.save_config_data
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
            self.xlrd_reader.xlrd_read_workbook_finished.connect(
                lambda sheets: self.showWorksheetListDlg(filename, sheets))
            self.xlrd_reader.xlrd_read_workbook_error.connect(
                lambda e: qtw.QMessageBox.critical(
                    self,
                    'Error Occurred',
                    str(e)
                )
            )
            self.xlrdDialog = NotificationDialog(self,
                                                 'Action in Progress',
                                                 'Scanning the Excel file, please wait..')
            self.xlrd_reader.started.connect(self.xlrdDialog.show)
            self.xlrd_reader.finished.connect(self.xlrdDialog.close)
            self.xlrd_reader.start()

    # TODO: use a better method name
    def showWorksheetListDlg(self, filename, worksheets):
        worksheet, ok = qtw.QInputDialog.getItem(
            self,
            'Select a worksheet',
            'Worksheets',
            worksheets,
            0,
            False
        )
        if worksheet and ok:
            self.pandas_excel_reader = PandasReadExcelThread(filename, worksheet)
            self.pandas_excel_reader.pandas_read_excel_finished.connect(self.read_from_excel_action)
            pandasExcelDialog = NotificationDialog(self, 'Action in Progress', 'Reading data, please wait..')
            self.pandas_excel_reader.started.connect(pandasExcelDialog.show)
            self.pandas_excel_reader.finished.connect(pandasExcelDialog.close)
            self.pandas_excel_reader.start()

    def read_from_excel_action(self, df):
        drug_data = yaml.load(open('drugs.yaml'), Loader=yaml.Loader)
        self.dataframe = PandasModel(df, head_row=20)
        self.data_table.setModel(self.dataframe)
        self.column_items = []
        aliases = self.config_data.get('aliases', {})
        descs = self.config_data.get('descs', {})
        keep_columns = self.config_data.get('keep_columns', [])
        drug_abbrs = []
        for group, drugs in drug_data.items():
            for drug in drugs:
                name, abbrs = drug.split(';')
                drug_abbrs += abbrs.split(',')

        if keep_columns:
            no_kept_columns = False
        else:
            no_kept_columns = True

        for n, col in enumerate(self.data_table.model().columns):
            citem = qtw.QTreeWidgetItem(self.column_treewidget)
            citem.setText(0, col)
            citem.setText(5, aliases.get(col, col))
            citem.setText(6, descs.get(col, ''))

            if no_kept_columns:
                keep_columns.append(col)
                citem.setCheckState(0, qtc.Qt.Checked)
            else:
                if col in keep_columns:
                    citem.setCheckState(0, qtc.Qt.Checked)
                else:
                    citem.setCheckState(0, qtc.Qt.Unchecked)

            if col in self.config_data.get('key_columns', []):
                citem.setCheckState(1, qtc.Qt.Checked)
            else:
                citem.setCheckState(1, qtc.Qt.Unchecked)

            if col in self.config_data.get('date_columns', []):
                citem.setCheckState(2, qtc.Qt.Checked)
            else:
                citem.setCheckState(2, qtc.Qt.Unchecked)

            if (len(self.config_data.get('drug_columns', [])) == 0 and col in drug_abbrs):
                citem.setCheckState(3, qtc.Qt.Checked)
            elif col in self.config_data.get('drug_columns', []):
                citem.setCheckState(3, qtc.Qt.Checked)
            else:
                citem.setCheckState(3, qtc.Qt.Unchecked)

            if col == self.config_data.get('organism_column', ''):
                citem.setCheckState(4, qtc.Qt.Checked)
            else:
                citem.setCheckState(4, qtc.Qt.Unchecked)

            citem.setFlags(citem.flags() | qtc.Qt.ItemIsEditable)
            self.column_items.append(citem)

        self.config_data['keep_columns'] = keep_columns

    def column_treewidget_item_clicked(self, item, ncol):
        colname = item.text(0)
        if ncol == 1:
            key_columns = self.config_data.get('key_columns', [])
            if item.checkState(ncol) == qtc.Qt.Checked:
                if colname not in key_columns:
                    key_columns.append(colname)
                    self.config_data['key_columns'] = key_columns
            else:
                if colname in key_columns:
                    key_columns.remove(colname)
                self.config_data['key_columns'] = key_columns
        elif ncol == 0:
            keep_columns = self.config_data.get('keep_columns', [])
            if item.checkState(ncol) == qtc.Qt.Checked:
                if colname not in keep_columns:
                    keep_columns.append(colname)
                    self.config_data['keep_columns'] = keep_columns
            else:
                if colname in keep_columns:
                    keep_columns.remove(colname)
                self.config_data['keep_columns'] = keep_columns
        elif ncol == 2:
            date_columns = self.config_data.get('date_columns', [])
            if item.checkState(ncol) == qtc.Qt.Checked:
                if not is_datetime64_any_dtype(self.data_table.model().data[colname]):
                    response = qtw.QMessageBox.warning(
                        self,
                        'Invalid Date Data',
                        'Dates in this column may not be valid.'
                        '\nYou can use Excel to create valid dates from data in this column.',
                        qtw.QMessageBox.Abort
                    )
                    if response == qtw.QMessageBox.Abort:
                        item.setCheckState(2, qtc.Qt.Unchecked)
                else:
                    if colname not in date_columns:
                        date_columns.append(colname)
                    self.config_data['date_columns'] = date_columns
            else:
                if colname in date_columns:
                    date_columns.remove(colname)
                self.config_data['date_columns'] = date_columns
        elif ncol == 3:
            drug_columns = self.config_data.get('drug_columns', [])
            if item.checkState(ncol) == qtc.Qt.Checked:
                if colname not in drug_columns:
                    drug_columns.append(colname)
                    self.config_data['drug_columns'] = drug_columns
            else:
                if colname in drug_columns:
                    drug_columns.remove(colname)
                self.config_data['drug_columns'] = drug_columns
        elif ncol == 4:
            organism_column = self.config_data.get('organism_column', '')
            if item.checkState(ncol) == qtc.Qt.Checked:
                if colname != organism_column:
                    self.config_data['organism_column'] = colname
            else:
                if colname == organism_column:
                    self.config_data['organism_column'] = ''

    def column_treewidget_current_item_changed(self):
        column = self.column_treewidget.currentItem().text(0)
        self.info_textedit.setText(str(self.data_table.model().describe(column)))
        self.data_table.selectColumn(self.data_table.model().columns.to_list().index(column))

    @qtc.pyqtSlot(int)
    def data_table_column_changed(self, colindex):
        self.column_treewidget.setCurrentItem(self.column_items[colindex])
        print(colindex)

    @qtc.pyqtSlot(qtc.QModelIndex)
    def data_table_item_changed(self, curindex):
        print(curindex.column())

    def save_config_data(self):
        config_filepath = os.path.join(self.settings.value('current_proj_dir'), 'config.yml')
        aliases = {}
        descs = {}
        for citem in self.column_items:
            aliases[citem.text(0)] = citem.text(5)
            descs[citem.text(0)] = citem.text(6)
        self.config_data['aliases'] = aliases
        self.config_data['descs'] = descs
        try:
            yaml.dump(self.config_data,
                      stream=open(config_filepath, 'w'),
                      Dumper=yaml.Dumper)
        except Exception as e:
            response = qtw.QMessageBox.critical(
                self,
                'Error Occurred',
                str(e),
                qtw.QMessageBox.Abort
            )
        else:
            qtw.QMessageBox.information(
                self,
                'Finished',
                'Project profile have been saved.',
                qtw.QMessageBox.Ok
            )

    @qtc.pyqtSlot()
    def showGroupValuesDialog(self):
        dialog = qtw.QDialog(self)
        colname, ok = qtw.QInputDialog.getItem(
            self,
            'Select column',
            'Columns',
            self.config_data['keep_columns'],
            False
        )
        if not ok:
            return

        dialog.colname = colname
        dialog.groups = {}
        dialog.vlayout = qtw.QVBoxLayout()
        dialog.setLayout(dialog.vlayout)
        dialog.hlayout = qtw.QHBoxLayout()
        dialog.coltree = qtw.QTreeWidget()
        dialog.coltree.setHeaderLabels(['Column'])
        dialog.coltree.setAlternatingRowColors(True)

        if colname and ok:
            for val in self.data_table.model().data[colname].unique():
                item = qtw.QTreeWidgetItem(dialog.coltree)
                item.setText(0, val)

        dialog.grouptree = qtw.QTreeWidget()
        dialog.grouptree.setHeaderLabels(['Group', 'Column'])
        dialog.grouptree.setAlternatingRowColors(True)
        dialog.button_vlayout = qtw.QVBoxLayout()  # two buttons between the list widgets
        left_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Button_Back.png'),
            '',
            dialog,
            clicked=lambda: self.move_item_back_from_group(dialog)
        )
        left_btn.setStyleSheet(
            'QPushButton {border: none;}'
        )
        left_btn.setIconSize(qtc.QSize(48, 48))
        right_btn = qtw.QPushButton(
            qtg.QIcon('../icons/Koloria-Icon-Set/Button_Next.png'),
            '',
            dialog,
            clicked=lambda: self.move_item_to_group(dialog)
        )
        right_btn.setStyleSheet(
            'QPushButton {border: none;}'
        )
        right_btn.setIconSize(qtc.QSize(48, 48))
        dialog.button_vlayout.addWidget(left_btn)
        dialog.button_vlayout.addWidget(right_btn)
        dialog.hlayout.addWidget(dialog.coltree)
        dialog.hlayout.addLayout(dialog.button_vlayout)
        dialog.hlayout.addWidget(dialog.grouptree)
        dialog.vlayout.addLayout(dialog.hlayout)
        dialog.button_box = qtw.QDialogButtonBox(dialog)
        dialog.button_box.setStandardButtons(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)
        dialog.button_box.accepted.connect(lambda: self.show_create_new_group_column_dialog(dialog))
        dialog.button_box.rejected.connect(lambda: dialog.close)
        dialog.vlayout.addWidget(dialog.button_box)

        dialog.button_group = qtw.QGroupBox('Edit')
        dialog.button_group_layout = qtw.QVBoxLayout()
        dialog.button_group_layout.setAlignment(qtc.Qt.AlignTop)
        dialog.button_group.setLayout(dialog.button_group_layout)
        add_group_btn = qtw.QPushButton('Add group', dialog.button_group)
        add_group_btn.clicked.connect(lambda: self.open_add_group_dialog(dialog))
        remove_group_btn = qtw.QPushButton('Remove group', dialog.button_group)
        dialog.button_group_layout.addWidget(add_group_btn)
        dialog.button_group_layout.addWidget(remove_group_btn)
        dialog.hlayout.addWidget(dialog.button_group)
        dialog.show()

    def open_add_group_dialog(self, dialog):
        group, ok = qtw.QInputDialog.getText(
            self,
            'New Group',
            'Group'
        )
        if group and ok:
            item = qtw.QTreeWidgetItem(dialog.grouptree)
            item.setText(0, group)

    def move_item_to_group(self, dialog):
        curcol_item = dialog.coltree.currentItem()
        curgroup_item = dialog.grouptree.currentItem()
        if curgroup_item is None or curcol_item is None:
            qtw.QMessageBox.critical(
                dialog,
                'No values selected',
                'Please choose a value and a group.'
            )
            return

        curcol_item_idx = dialog.coltree.indexOfTopLevelItem(curcol_item)
        curcol_item_without_parent = dialog.coltree.takeTopLevelItem(curcol_item_idx)
        curgroup_item.addChild(curcol_item_without_parent)
        dialog.groups[curcol_item.text(0)] = curgroup_item.text(0)

    def move_item_back_from_group(self, dialog):
        curgroup_item = dialog.grouptree.currentItem()
        if curgroup_item is None:
            qtw.QMessageBox.critical(
                dialog,
                'No value selected',
                'Please choose a value.'
            )
            return

        if curgroup_item.parent():
            idx = curgroup_item.parent().indexOfChild(curgroup_item)
            item_without_parent = curgroup_item.parent().takeChild(idx)
            dialog.coltree.addTopLevelItem(item_without_parent)
            dialog.groups.pop(curgroup_item.text(0))

    def show_create_new_group_column_dialog(self, dialog):
        def close_dialogs(form, dialog):
            form.close()
            dialog.close()

        def create_new_column(self, form, dialog):
            df = self.data_table.model().data
            colname_idx = df.columns.get_loc(dialog.colname)
            if form.default_edit.text() == '':
                data = df[dialog.colname].apply(lambda x: dialog.groups.get(x, x))
                df.insert(colname_idx + 1, form.colname_edit.text(), data)
            else:
                default = form.default_edit.text()
                data = df[dialog.colname].apply(lambda x: dialog.groups.get(x, default))
                df.insert(colname_idx + 1, form.colname_edit.text(), data)
            self.data_table.model().layoutChanged.emit()
            close_dialogs(form, dialog)


        form = qtw.QDialog(self)
        form.setLayout(qtw.QVBoxLayout())
        form_layout = qtw.QFormLayout()
        form.colname_edit = qtw.QLineEdit()
        form.default_edit = qtw.QLineEdit()
        form_layout.addRow('Column Name', form.colname_edit)
        form_layout.addRow('Default Value', form.default_edit)
        form.button_box = qtw.QDialogButtonBox()
        form.button_box.setStandardButtons(
            qtw.QDialogButtonBox.Save | qtw.QDialogButtonBox.Cancel
        )
        form.button_box.accepted.connect(lambda: create_new_column(self, form, dialog))
        form.button_box.rejected.connect(dialog.close)
        form.layout().addLayout(form_layout)
        form.layout().addWidget(form.button_box)
        form.setModal(True)
        form.show()

    def showDrugRegistryDialog(self):
        self.drug_data = yaml.load(open('drugs.yaml', 'r'), Loader=yaml.Loader)
        self.drug_dialog = qtw.QDialog(self)
        self.drug_dialog.setWindowTitle('Drug Registry')
        edit_buttons = qtw.QGroupBox('Edit')
        edit_buttons.setLayout(qtw.QVBoxLayout())
        add_group_btn = qtw.QPushButton('Add drug group')
        add_group_btn.clicked.connect(self.add_drug_group)
        add_btn = qtw.QPushButton('Add drug')
        add_btn.clicked.connect(self.show_add_drug_dialog)
        remove_btn = qtw.QPushButton('Remove')
        remove_btn.clicked.connect(self.remove_drug_item)
        edit_btn = qtw.QPushButton('Edit')
        edit_btn.clicked.connect(self.show_edit_drug_dialog)
        help_btn = qtw.QPushButton(qtg.QIcon('../icons/Koloria-Icon-Set/Help.png'), 'Help')
        edit_buttons.layout().addWidget(add_group_btn)
        edit_buttons.layout().addWidget(add_btn)
        edit_buttons.layout().addWidget(remove_btn)
        edit_buttons.layout().addWidget(edit_btn)
        edit_buttons.layout().addWidget(help_btn)
        button_box = qtw.QDialogButtonBox()
        button_box.addButton('Save', button_box.AcceptRole)
        button_box.addButton('Cancel', button_box.RejectRole)
        button_box.accepted.connect(self.save_drug_registry)
        button_box.rejected.connect(self.drug_dialog.close)
        list_layout = qtw.QHBoxLayout()

        self.drug_list = qtw.QTreeWidget()
        self.drug_list.setHeaderLabels(['Name', 'Abbreviation'])
        self.drug_list.doubleClicked.connect(self.show_edit_drug_dialog)
        drug_items = defaultdict(list)
        drug_group_items = {}
        for drug_group in self.drug_data:
            drug_group_item = qtw.QTreeWidgetItem(self.drug_list)
            drug_group_item.setText(0, drug_group)
            drug_group_items[drug_group] = drug_group_item
            for drug in self.drug_data[drug_group]:
                drug_name, abbrs = drug.split(';')
                drug_item = qtw.QTreeWidgetItem(drug_group_item)
                drug_item.setText(0, drug_name)
                drug_item.setText(1, abbrs)
                drug_items[drug_group].append(drug_item)

        list_layout.addWidget(self.drug_list)
        list_layout.addWidget(edit_buttons)
        self.drug_dialog.setLayout(qtw.QVBoxLayout())
        self.drug_dialog.layout().addLayout(list_layout)
        self.drug_dialog.layout().addWidget(button_box)
        self.drug_dialog.resize(600, 300)
        self.drug_dialog.setModal(True)
        self.drug_dialog.show()

    def save_drug_registry(self):
        yaml.dump(self.drug_data, stream=open('drugs.yaml', 'w'), Dumper=yaml.Dumper)
        self.drug_dialog.close()

    def add_drug_group(self):
        drug_group_name, Ok = qtw.QInputDialog.getText(self,
                                                       'Add Drug Group', 'Drug group:',
                                                       qtw.QLineEdit.Normal)
        if Ok and drug_group_name != '':
            self.drug_data[drug_group_name] = []
            item = qtw.QTreeWidgetItem()
            item.setText(0, drug_group_name)
            self.drug_list.addTopLevelItem(item)

    def show_add_drug_dialog(self):
        dialog = qtw.QDialog(self)
        layout = qtw.QVBoxLayout()
        form = qtw.QFormLayout()
        button_box = qtw.QDialogButtonBox()
        button_box.setStandardButtons(button_box.Save | button_box.Cancel)
        button_box.accepted.connect(lambda: self.add_drug(dialog))
        button_box.rejected.connect(dialog.close)
        dialog.drug_name_line_edit = qtw.QLineEdit()
        dialog.drug_abbr_line_edit = qtw.QLineEdit()
        form.addRow('Name', dialog.drug_name_line_edit)
        form.addRow('Abbreviation', dialog.drug_abbr_line_edit)
        layout.addLayout(form)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.setModal(True)
        dialog.show()

    def add_drug(self, dialog):
        drug_group_item = self.drug_list.currentItem()
        if drug_group_item.text(0) not in self.drug_data:
            drug_group_item = drug_group_item.parent()

        name = dialog.drug_name_line_edit.text()
        abbrs = ','.join([ab.strip() for ab in dialog.drug_abbr_line_edit.text().split(',')])
        if name != '' and abbrs != '':
            drug_info = u'{};{}'.format(name,abbrs)
            drug_item = qtw.QTreeWidgetItem()
            drug_item.setText(0, name)
            drug_item.setText(1, abbrs)
            drug_group_item.addChild(drug_item)
            self.drug_data[drug_group_item.text(0)].append(drug_info)

        dialog.close()

    def show_edit_drug_dialog(self):
        curitem = self.drug_list.currentItem()
        dialog = qtw.QDialog(self)
        layout = qtw.QVBoxLayout()
        form = qtw.QFormLayout()
        button_box = qtw.QDialogButtonBox()
        button_box.setStandardButtons(button_box.Save | button_box.Cancel)
        button_box.accepted.connect(lambda: self.edit_drug(dialog))
        button_box.rejected.connect(dialog.close)
        dialog.drug_name_line_edit = qtw.QLineEdit(curitem.text(0))
        if curitem.text(0) not in self.drug_data:
            dialog.drug_abbr_line_edit = qtw.QLineEdit(curitem.text(1))
        else:
            dialog.drug_abbr_line_edit = qtw.QLineEdit()
            dialog.drug_abbr_line_edit.setDisabled(True)
        form.addRow('Name', dialog.drug_name_line_edit)
        form.addRow('Abbreviation', dialog.drug_abbr_line_edit)
        layout.addLayout(form)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.setModal(True)
        dialog.show()

    def edit_drug(self, dialog):
        curitem = self.drug_list.currentItem()
        if curitem.text(0) in self.drug_data:
            drugs = self.drug_data.pop(curitem.text(0))
            self.drug_data[dialog.drug_name_line_edit.text()] = drugs
            curitem.setText(0, dialog.drug_name_line_edit.text())
        else:
            curitem.setText(0, dialog.drug_name_line_edit.text())
            curitem.setText(1, dialog.drug_abbr_line_edit.text())
            for group in self.drug_data:
                for drug in self.drug_data[group]:
                    if drug.startswith(dialog.drug_name_line_edit.text()):
                        self.drug_data[group].remove(drug)
                        self.drug_data[group].append(u'{};{}'.format(
                            dialog.drug_name_line_edit.text(),
                            ','.join([a.strip() for a in dialog.drug_abbr_line_edit.text().split(',')])
                        ))
        dialog.close()

    def remove_drug_item(self):
        item = self.drug_list.currentItem()
        root = self.drug_list.invisibleRootItem()
        if item.text(0) in self.drug_data:
            item_ = self.drug_data.pop(item.text(0))
            root.removeChild(item)
        else:
            item.parent().removeChild(item)
            for group in self.drug_data:
                for drug in self.drug_data[group]:
                    if drug.startswith(item.text(0)):
                        self.drug_data[group].remove(drug)

    def showOrgRegistryDialog(self):
        self.org_data = yaml.load(open('organisms.yaml', 'r'), Loader=yaml.Loader)
        if self.org_data is None:
            self.org_data = {}
        self.org_dialog = qtw.QDialog()
        self.org_dialog.setWindowTitle('Organism Registry')
        self.org_dialog.main_layout = qtw.QVBoxLayout()
        self.org_dialog.h_layout = qtw.QHBoxLayout()
        self.org_dialog.setLayout(self.org_dialog.main_layout)
        self.org_dialog.org_tr = qtw.QTreeWidget()
        self.org_dialog.org_tr.setAlternatingRowColors(True)
        self.org_dialog.org_tr.setSelectionMode(qtw.QAbstractItemView.SingleSelection)
        self.org_dialog.org_tr.setHeaderLabels(['Code', 'Group', 'Gram', 'Genus',
                                                'Species', 'Subspecies', 'Property',
                                                'Note'])
        self.org_dialog.org_tr.doubleClicked.connect(self.show_edit_organism_dialog)

        if self.org_data:
            for org in self.org_data.values():
                item = qtw.QTreeWidgetItem()
                item.setText(0, org.get('code'))
                item.setText(1, org.get('group'))
                item.setText(2, org.get('gram'))
                item.setText(3, org.get('genus'))
                item.setText(4, org.get('species'))
                item.setText(5, org.get('subspecies'))
                item.setText(6, org.get('property'))
                item.setText(7, org.get('note'))
                self.org_dialog.org_tr.addTopLevelItem(item)

        self.org_dialog.button_group = qtw.QGroupBox('Edit')
        self.org_dialog.group_box_layout = qtw.QVBoxLayout()
        self.org_dialog.group_box_layout.setAlignment(qtc.Qt.AlignTop)
        self.org_dialog.button_group.setLayout(self.org_dialog.group_box_layout)
        add_org_btn = qtw.QPushButton('Add', self.org_dialog.button_group)
        add_org_btn.clicked.connect(self.show_add_organism_dialog)
        import_org_btn = qtw.QPushButton('Import', self.org_dialog.button_group)
        import_org_btn.clicked.connect(self.show_import_organism_dialog)
        edit_org_btn = qtw.QPushButton('Edit', self.org_dialog.button_group)
        edit_org_btn.clicked.connect(self.show_edit_organism_dialog)
        remove_btn = qtw.QPushButton('Remove', self.org_dialog.button_group)
        remove_btn.clicked.connect(self.remove_org)
        self.org_dialog.group_box_layout.addWidget(import_org_btn)
        self.org_dialog.group_box_layout.addWidget(add_org_btn)
        self.org_dialog.group_box_layout.addWidget(edit_org_btn)
        self.org_dialog.group_box_layout.addWidget(remove_btn)
        self.org_dialog.button_box = qtw.QDialogButtonBox()
        self.org_dialog.button_box.addButton('Save', qtw.QDialogButtonBox.AcceptRole)
        self.org_dialog.button_box.addButton('Cancel', qtw.QDialogButtonBox.RejectRole)
        self.org_dialog.button_box.accepted.connect(self.save_org_registry)
        self.org_dialog.button_box.rejected.connect(self.org_dialog.close)
        self.org_dialog.h_layout.addWidget(self.org_dialog.org_tr)
        self.org_dialog.h_layout.addWidget(self.org_dialog.button_group)
        self.org_dialog.layout().addLayout(self.org_dialog.h_layout)
        self.org_dialog.layout().addWidget(self.org_dialog.button_box)
        self.org_dialog.resize(800, 400)
        self.org_dialog.setModal(False)
        self.org_dialog.show()

    def show_add_organism_dialog(self):
        form = qtw.QDialog(self)
        form.setLayout(qtw.QVBoxLayout())
        form_layout = qtw.QFormLayout()
        form.code_edit = qtw.QLineEdit()
        form.group_edit = qtw.QLineEdit()
        form.gram_edit = qtw.QLineEdit()
        form.genus_edit = qtw.QLineEdit()
        form.species_edit = qtw.QLineEdit()
        form.subspecies_edit = qtw.QLineEdit()
        form.property_edit = qtw.QLineEdit()
        form.note_edit = qtw.QLineEdit()
        form_layout.addRow('Code', form.code_edit)
        form_layout.addRow('Group', form.group_edit)
        form_layout.addRow('Gram', form.gram_edit)
        form_layout.addRow('Genus', form.genus_edit)
        form_layout.addRow('Species', form.species_edit)
        form_layout.addRow('Subspecies', form.subspecies_edit)
        form_layout.addRow('Property', form.property_edit)
        form_layout.addRow('Note', form.note_edit)
        form.layout().addLayout(form_layout)
        button_box = qtw.QDialogButtonBox()
        button_box.addButton('Add', qtw.QDialogButtonBox.AcceptRole)
        button_box.addButton('Cancel', qtw.QDialogButtonBox.RejectRole)
        button_box.accepted.connect(lambda: self.add_organism(form))
        button_box.rejected.connect(form.close)
        form.layout().addWidget(button_box)
        form.setModal(True)
        form.show()

    def add_organism(self, form, exists=False):
        if exists:
            curitem = self.org_dialog.org_tr.currentItem()
            self.org_data.pop(curitem.text(0))
            idx = self.org_dialog.org_tr.indexOfTopLevelItem(curitem)
            self.org_dialog.org_tr.takeTopLevelItem(idx)

        item = qtw.QTreeWidgetItem()
        if (form.code_edit.text() and (form.genus_edit.text() or form.group_edit.text())):
            self.org_data[form.code_edit.text()] = {
                'code': form.code_edit.text(),
                'group': form.group_edit.text(),
                'gram': form.gram_edit.text(),
                'genus': form.genus_edit.text(),
                'species': form.species_edit.text(),
                'subspecies': form.subspecies_edit.text(),
                'property': form.property_edit.text(),
                'note': form.note_edit.text(),
            }
            item.setText(0, form.code_edit.text())
            item.setText(1, form.group_edit.text())
            item.setText(2, form.gram_edit.text())
            item.setText(3, form.genus_edit.text())
            item.setText(4, form.species_edit.text())
            item.setText(5, form.subspecies_edit.text())
            item.setText(6, form.property_edit.text())
            item.setText(7, form.note_edit.text())
            self.org_dialog.org_tr.addTopLevelItem(item)
            form.close()
        else:
            qtw.QMessageBox.warning(
                self,
                'Not enough information',
                'At least code, genus or group must be given.',
                qtw.QMessageBox.Abort
            )

    def show_import_organism_dialog(self):
        filename, type_ = qtw.QFileDialog.getOpenFileName(
            self.org_dialog, 'Import Organisms',
            self.settings.value('current_proj_dir'),
            'Excel files (*.xls *xlsx)'
        )
        if filename:
            org_df = pd.read_excel(filename).fillna('')
            for idx, row in org_df.iterrows():
                item = qtw.QTreeWidgetItem()
                if row.get('code') and (row.get('genus') or row.get('group')):
                    item.setText(0, row.get('code'))
                    item.setText(1, row.get('group'))
                    item.setText(2, row.get('gram'))
                    item.setText(3, row.get('genus'))
                    item.setText(4, row.get('species'))
                    item.setText(5, row.get('subspecies'))
                    item.setText(6, row.get('property'))
                    item.setText(7, row.get('note'))
                    self.org_dialog.org_tr.addTopLevelItem(item)
                    self.org_data[row.get('code')] = row.to_dict()

    def remove_org(self):
        curitem = self.org_dialog.org_tr.currentItem()
        index = self.org_dialog.org_tr.indexOfTopLevelItem(curitem)
        self.org_dialog.org_tr.takeTopLevelItem(index)

    def show_edit_organism_dialog(self):
        curitem = self.org_dialog.org_tr.currentItem()
        form = qtw.QDialog(self)
        form.setLayout(qtw.QVBoxLayout())
        form_layout = qtw.QFormLayout()
        form.code_edit = qtw.QLineEdit(curitem.text(0))
        form.group_edit = qtw.QLineEdit(curitem.text(1))
        form.gram_edit = qtw.QLineEdit(curitem.text(2))
        form.genus_edit = qtw.QLineEdit(curitem.text(3))
        form.species_edit = qtw.QLineEdit(curitem.text(4))
        form.subspecies_edit = qtw.QLineEdit(curitem.text(5))
        form.property_edit = qtw.QLineEdit(curitem.text(6))
        form.note_edit = qtw.QLineEdit(curitem.text(7))
        form_layout.addRow('Code', form.code_edit)
        form_layout.addRow('Group', form.group_edit)
        form_layout.addRow('Gram', form.gram_edit)
        form_layout.addRow('Genus', form.genus_edit)
        form_layout.addRow('Species', form.species_edit)
        form_layout.addRow('Subspecies', form.subspecies_edit)
        form_layout.addRow('Property', form.property_edit)
        form_layout.addRow('Note', form.note_edit)
        form.layout().addLayout(form_layout)
        button_box = qtw.QDialogButtonBox()
        button_box.addButton('Add', qtw.QDialogButtonBox.AcceptRole)
        button_box.addButton('Cancel', qtw.QDialogButtonBox.RejectRole)
        button_box.accepted.connect(lambda: self.add_organism(form, exists=True))
        button_box.rejected.connect(form.close)
        form.layout().addWidget(button_box)
        form.setModal(True)
        form.show()

    def save_org_registry(self):
        yaml.dump(self.org_data, stream=open('organisms.yaml', 'w'), Dumper=yaml.Dumper)
        self.org_dialog.close()


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
        button_box = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Save | qtw.QDialogButtonBox.Cancel)
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
