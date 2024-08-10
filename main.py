import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                             QCheckBox, QMenuBar, QMenu, QFileDialog, QInputDialog, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import re
import numpy as np
from scipy import interpolate

class PlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Line Plotter with Enhanced Superscript")
        self.setGeometry(100, 100, 900, 600)

        self.graph_title = "Line Plot"
        self.plot_style = "Connecting Lines"

        # Create menu bar
        self.create_menu_bar()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create left panel for data input
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel)

        # Create table for data entry
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['X', 'Y'])
        left_layout.addWidget(self.table)

        # Create 'Add Row' button
        add_row_button = QPushButton('Add Row')
        add_row_button.clicked.connect(self.add_row)
        left_layout.addWidget(add_row_button)

        # Create input fields for axis labels
        x_axis_layout = QHBoxLayout()
        x_axis_layout.addWidget(QLabel('X-axis label:'))
        self.x_axis_input = QLineEdit()
        x_axis_layout.addWidget(self.x_axis_input)
        left_layout.addLayout(x_axis_layout)

        y_axis_layout = QHBoxLayout()
        y_axis_layout.addWidget(QLabel('Y-axis label:'))
        self.y_axis_input = QLineEdit()
        y_axis_layout.addWidget(self.y_axis_input)
        left_layout.addLayout(y_axis_layout)

        # Add plot style dropdown
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel('Plot Style:'))
        self.style_dropdown = QComboBox()
        self.style_dropdown.addItems(["Connecting Lines", "Smooth Curve"])
        style_layout.addWidget(self.style_dropdown)
        left_layout.addLayout(style_layout)

        # Add LaTeX checkbox
        self.latex_checkbox = QCheckBox("Use LaTeX rendering (if available)")
        left_layout.addWidget(self.latex_checkbox)

        # Add LaTeX usage hint
        self.latex_hint = QLabel("Hint: Use $ $ for inline LaTeX. E.g., $x^2$ for x²")
        self.latex_hint.setVisible(False)
        left_layout.addWidget(self.latex_hint)

        # Connect checkbox to hint visibility
        self.latex_checkbox.stateChanged.connect(self.toggle_latex_hint)

        # Create 'Plot' button
        plot_button = QPushButton('Plot')
        plot_button.clicked.connect(self.plot_data)
        left_layout.addWidget(plot_button)

        # Create right panel for plot display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel)

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Save action
        save_action = QAction("Save Plot", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_plot)
        file_menu.addAction(save_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        # Set Title action
        set_title_action = QAction("Set Graph Title", self)
        set_title_action.triggered.connect(self.set_graph_title)
        edit_menu.addAction(set_title_action)

    def save_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            self.figure.savefig(file_path, bbox_inches='tight')
            print(f"Plot saved as {file_path}")

    def set_graph_title(self):
        title, ok = QInputDialog.getText(self, "Set Graph Title", "Enter graph title:")
        if ok and title:
            self.graph_title = title
            self.plot_data()  # Redraw the plot with the new title

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

    def toggle_latex_hint(self, state):
        self.latex_hint.setVisible(state == Qt.CheckState.Checked.value)

    def format_superscript(self, text):
        superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ',
            'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 'p': 'ᵖ', 'q': 'q', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ',
            'u': 'ᵘ', 'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ',
            'A': 'ᴬ', 'B': 'ᴮ', 'C': 'ᶜ', 'D': 'ᴰ', 'E': 'ᴱ', 'F': 'ᶠ', 'G': 'ᴳ', 'H': 'ᴴ', 'I': 'ᴵ', 'J': 'ᴶ',
            'K': 'ᴷ', 'L': 'ᴸ', 'M': 'ᴹ', 'N': 'ᴺ', 'O': 'ᴼ', 'P': 'ᴾ', 'Q': 'Q', 'R': 'ᴿ', 'S': 'ˢ', 'T': 'ᵀ',
            'U': 'ᵁ', 'V': 'ⱽ', 'W': 'ᵂ', 'X': 'ˣ', 'Y': 'ʸ', 'Z': 'ᶻ',
            '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾', ':': '︓', '>': '˃', '<': '˂', '/': 'ᐟ', '\\': '˂'
        }
        
        def replace_superscript(match):
            exp = match.group(1)
            if exp.startswith('(') and exp.endswith(')'):
                exp = exp[1:-1]  # Remove parentheses
            return ''.join(superscript_map.get(char, char) for char in exp)

        # Replace patterns like x^-3, x^(2+3), x^abc, etc.
        return re.sub(r'\^(-?\d+|\(-?[^()]+\)|[a-zA-Z]+)', replace_superscript, text)

    def plot_data(self):
        x_values = []
        y_values = []

        for row in range(self.table.rowCount()):
            try:
                x_item = self.table.item(row, 0)
                y_item = self.table.item(row, 1)
                if x_item and y_item:
                    x = float(x_item.text())
                    y = float(y_item.text())
                    x_values.append(x)
                    y_values.append(y)
            except ValueError:
                print(f"Invalid data in row {row + 1}")

        if len(x_values) < 2:
            print("Please enter at least two valid data points")
            return

        self.ax.clear()
        
        # Sort the points by x-value
        points = sorted(zip(x_values, y_values))
        x_values, y_values = zip(*points)

        if self.style_dropdown.currentText() == "Connecting Lines":
            self.ax.plot(x_values, y_values, 'bo-')
        else:  # Smooth Curve
            x_new = np.linspace(min(x_values), max(x_values), 300)
            f = interpolate.interp1d(x_values, y_values, kind='cubic')
            y_smooth = f(x_new)
            self.ax.plot(x_new, y_smooth, 'b-')
            self.ax.plot(x_values, y_values, 'bo')  # Add original points
        
        x_label = self.x_axis_input.text() or 'X'
        y_label = self.y_axis_input.text() or 'Y'
        
        if self.latex_checkbox.isChecked():
            try:
                matplotlib.rcParams['text.usetex'] = True
                matplotlib.rcParams['font.family'] = 'serif'
                self.ax.set_xlabel(f'${x_label}$')
                self.ax.set_ylabel(f'${y_label}$')
                self.ax.set_title(f'${self.graph_title}$')
            except Exception as e:
                print(f"LaTeX rendering failed: {e}")
                print("Falling back to standard text rendering with superscript formatting")
                matplotlib.rcParams['text.usetex'] = False
                self.ax.set_xlabel(self.format_superscript(x_label))
                self.ax.set_ylabel(self.format_superscript(y_label))
                self.ax.set_title(self.format_superscript(self.graph_title))
        else:
            matplotlib.rcParams['text.usetex'] = False
            self.ax.set_xlabel(self.format_superscript(x_label))
            self.ax.set_ylabel(self.format_superscript(y_label))
            self.ax.set_title(self.format_superscript(self.graph_title))

        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotterApp()
    window.show()
    sys.exit(app.exec())