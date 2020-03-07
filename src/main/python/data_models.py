import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import pandas as pd


class PandasModel(qtc.QAbstractTableModel):
    def __init__(self, dataframe, head_row=0):
        super(PandasModel, self).__init__()
        if head_row == 0:
            self.data = dataframe
        else:
            self.data = dataframe.head(head_row)

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.data.columns)

    @property
    def columns(self):
        return self.data.columns

    def describe(self, column):
        if self.data[column].dtype == 'object':
            return self.data[column].value_counts()
        else:
            return self.data[column].describe()

    def data(self, index, role):
        if role == qtc.Qt.DisplayRole:
            # convert data to string or date will not display
            return str(self.data.values[index.row(), index.column()])

    def headerData(self, section, orientation, role=None):
        if(
            orientation == qtc.Qt.Horizontal and role == qtc.Qt.DisplayRole
        ):
            return self.data.columns[section]
        else:
            return super(PandasModel, self).headerData(section, orientation, role)

