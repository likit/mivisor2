import os
from collections import defaultdict

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
        registry_menu = menubar.addMenu('Registry')
        drug_registry = registry_menu.addAction('Drug', self.showDrugRegistryDialog)
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


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(600, 450)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)