import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import pandas as pd


class PandasModel(qtc.QAbstractTableModel):
    def __init__(self, dataframe):
        super(PandasModel, self).__init__()
        self.data = dataframe

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.data.columns)

    def data(self, index, role):
        if role == qtc.Qt.DisplayRole:
            return self.data.iloc[index.row, index.column]

    def headerData(self, section, orientation, role=None):
        if(
            orientation == qtc.Qt.Horizontal and role == qtc.Qt.DisplayRole
        ):
            return self.columns[section]
        else:
            return super(PandasModel, self).headerData(section, orientation, role)
