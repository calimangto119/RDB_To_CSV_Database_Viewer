# RDB_To_CSV_Database_Viewer.py
#
# Copyright (c) 2025 Juan Rico
#
# Licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
# You may not modify this file or use it for commercial purposes without explicit permission,
# and you must give appropriate credit if sharing this work.
# For the full license text, see the LICENSE file or visit:
# https://creativecommons.org/licenses/by-nc-nd/4.0/
#
# Description:
#   This PyQt5 application allows users to load multiple SQLite RDB files (with the .rdb extension),
#   extract data from a table named "logdata", combine the data, and view it in a modern UI.
#   It also provides an option to export the combined data to a CSV file.
#   This version is intended for use on Windows.

import sys
import sqlite3
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QTableView, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt5.QtCore import QAbstractTableModel, Qt


class PandasModel(QAbstractTableModel):
    """
    A model to interface a pandas DataFrame with Qt's Table View.
    """
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._df.iat[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                try:
                    return str(self._df.columns[section])
                except (IndexError,):
                    return ""
            elif orientation == Qt.Vertical:
                try:
                    return str(self._df.index[section])
                except (IndexError,):
                    return ""
        return None


class DataApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RDB To CSV Database Viewer")
        self.resize(600, 600)

        # DataFrame to store combined data
        self.df = pd.DataFrame()

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Table view to display data
        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        # Button layout at the bottom
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Button to load multiple RDB files
        self.load_button = QPushButton("Load Multiple RDBs")
        self.load_button.clicked.connect(self.load_multiple_rdb)
        button_layout.addWidget(self.load_button)

        # Button to export data to CSV
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_csv)
        button_layout.addWidget(self.export_button)

    def load_multiple_rdb(self):
        """
        Open a file dialog to select multiple SQLite files (with .rdb extension),
        then read the "logdata" table from each file and combine them into one DataFrame.
        """
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select SQLite RDB Files",
            "",
            "SQLite DB Files (*.rdb);;All Files (*)",
            options=options
        )
        if file_paths:
            combined_df = pd.DataFrame()
            for file_path in file_paths:
                try:
                    conn = sqlite3.connect(file_path)
                    table_name = "logdata"  # Assuming the table is always named "logdata"
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                    conn.close()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error loading {file_path}:\n{str(e)}")
            self.df = combined_df
            self.update_table_view()

    def update_table_view(self):
        """Update the QTableView with the data from the DataFrame."""
        model = PandasModel(self.df)
        self.table_view.setModel(model)

    def export_csv(self):
        """Export the DataFrame to a CSV file."""
        if self.df.empty:
            QMessageBox.warning(self, "Warning", "No data to export!")
            return
        options = QFileDialog.Options()
        export_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV",
            "",
            "CSV Files (*.csv)",
            options=options
        )
        if export_path:
            try:
                self.df.to_csv(export_path, index=False)
                QMessageBox.information(self, "Export Successful", "The data was exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exporting CSV:\n{str(e)}")


def main():
    app = QApplication(sys.argv)

    # Set a modern dark Fusion theme
    app.setStyle("Fusion")
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)

    window = DataApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
