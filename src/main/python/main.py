import os
from collections import defaultdict

from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import project_dialogs as pjd

import sys
import yaml

import pandas as pd


class MainWindow(qtw.QMainWindow):
    settings = qtc.QSettings('MUMT', 'Mivisor2')
    show_group_value_dialog = qtc.pyqtSignal()
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Mivisor2')
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        help_menu = menubar.addMenu('Help')
        registry_menu = menubar.addMenu('Registry')
        tool_menu = menubar.addMenu('Tools')
        self.grouping_menu = tool_menu.addAction('Group values', self.show_group_value_dialog.emit)
        self.grouping_menu.setDisabled(True)
        drug_registry = registry_menu.addAction('Drug', self.showDrugRegistryDialog)
        organism_registry = registry_menu.addAction('Organism', self.showOrgRegistryDialog)
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

    def showOrgRegistryDialog(self):
        self.org_data = yaml.load(open('organisms.yaml', 'r'), Loader=yaml.Loader)
        if self.org_data is None:
            self.org_data = {}
        self.org_dialog = qtw.QDialog(self)
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
        self.grouping_menu.setEnabled(True)
        self.show_group_value_dialog.connect(main_project_window.showGroupValuesDialog)

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