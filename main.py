import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QCheckBox, QMenuBar, QMenu, QFileDialog, QInputDialog, QComboBox,
                             QSlider, QDialog, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import matplotlib
import re
import numpy as np
from scipy import interpolate
from scipy import stats
import pandas as pd
import csv


class PlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Line Plotter with Data Import")
        self.setGeometry(100, 100, 1000, 600)

        self.graph_title = "Line Plot"
        self.plot_style = "Connecting Lines"
        self.animation = None
        self.animation_speed = 500  # milliseconds

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
        import_button = QPushButton('Import Data')
        import_button.clicked.connect(self.import_data)
        left_layout.addWidget(import_button)
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
        self.style_dropdown.addItems(["Connecting Lines", "Smooth Curve", "Polynomial Fit"])
        style_layout.addWidget(self.style_dropdown)
        left_layout.addLayout(style_layout)

        # Add polynomial degree spinner
        poly_layout = QHBoxLayout()
        poly_layout.addWidget(QLabel('Polynomial Degree:'))
        self.poly_degree_spinner = QSpinBox()
        self.poly_degree_spinner.setMinimum(1)
        self.poly_degree_spinner.setMaximum(10)
        self.poly_degree_spinner.setValue(1)
        poly_layout.addWidget(self.poly_degree_spinner)
        left_layout.addLayout(poly_layout)

        # Add interpolation method dropdown
        interp_layout = QHBoxLayout()
        interp_layout.addWidget(QLabel('Interpolation:'))
        self.interp_dropdown = QComboBox()
        self.interp_dropdown.addItems(["linear", "quadratic", "cubic"])
        interp_layout.addWidget(self.interp_dropdown)
        left_layout.addLayout(interp_layout)

        # Add slider for number of interpolation points
        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel('Interpolation Points:'))
        self.points_slider = QSlider(Qt.Orientation.Horizontal)
        self.points_slider.setMinimum(100)
        self.points_slider.setMaximum(10000)  # Increased maximum to 10,000
        self.points_slider.setValue(1000)  # Set default to 1,000
        self.points_slider.setTickInterval(1000)
        self.points_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        points_layout.addWidget(self.points_slider)
        self.points_label = QLabel('1000')  # Add a label to show the current value
        points_layout.addWidget(self.points_label)
        left_layout.addLayout(points_layout)

        # Connect the slider to update the label
        self.points_slider.valueChanged.connect(self.update_points_label)

        # Add LaTeX checkbox
        self.latex_checkbox = QCheckBox("Use LaTeX rendering (if available)")
        left_layout.addWidget(self.latex_checkbox)

        # Add animation controls
        animation_layout = QHBoxLayout()
        self.animate_button = QPushButton('Animate Plot')
        self.animate_button.clicked.connect(self.toggle_animation)
        animation_layout.addWidget(self.animate_button)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(100)
        self.speed_slider.setMaximum(2000)
        self.speed_slider.setValue(self.animation_speed)
        self.speed_slider.setTickInterval(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.valueChanged.connect(self.update_animation_speed)
        animation_layout.addWidget(QLabel('Speed:'))
        animation_layout.addWidget(self.speed_slider)

        left_layout.addLayout(animation_layout)

        # Create 'Plot' button
        plot_button = QPushButton('Plot')
        plot_button.clicked.connect(self.plot_data)
        left_layout.addWidget(plot_button)

        # Add Best Fit Line Analysis button
        best_fit_button = QPushButton('Best Fit Line Analysis')
        best_fit_button.clicked.connect(self.open_best_fit_window)
        left_layout.addWidget(best_fit_button)

        # Create right panel for plot display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel)

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)
    def update_points_label(self, value):
        self.points_label.setText(str(value))
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Import action
        import_action = QAction("Import Data", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)

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

    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Data", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
        if file_path:
            if file_path.endswith('.csv'):
                self.import_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self.import_xlsx(file_path)

    def import_csv(self, file_path):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        self.process_imported_data(data)

    def import_xlsx(self, file_path):
        df = pd.read_excel(file_path, header=None)
        data = df.values.tolist()
        self.process_imported_data(data)

    def process_imported_data(self, data):
        if len(data[0]) != 2:
            QMessageBox.warning(self, "Invalid Data", "Please ensure your file contains exactly two columns of data.")
            return

        preview = "\n".join([f"{row[0]}, {row[1]}" for row in data[:5]])
        preview += "\n...\n" if len(data) > 5 else ""

        msg = QMessageBox()
        msg.setWindowTitle("Data Preview")
        msg.setText(f"Preview of the first 5 rows:\n\n{preview}\n\nDoes the first row contain headers?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        response = msg.exec()

        if response == QMessageBox.StandardButton.Cancel:
            return

        has_headers = response == QMessageBox.StandardButton.Yes

        self.table.setRowCount(0)  # Clear existing data
        start_row = 1 if has_headers else 0

        for row in data[start_row:]:
            self.add_row()
            self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(self.table.rowCount() - 1, 1, QTableWidgetItem(str(row[1])))

        if has_headers:
            self.x_axis_input.setText(str(data[0][0]))
            self.y_axis_input.setText(str(data[0][1]))

        QMessageBox.information(self, "Import Successful", f"Imported {self.table.rowCount()} rows of data.")

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

        return re.sub(r'\^(-?\d+|\(-?[^()]+\)|[a-zA-Z]+)', replace_superscript, text)

    def get_plot_data(self):
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

        # Sort the points by x-value, but keep duplicates
        points = sorted(zip(x_values, y_values), key=lambda p: p[0])
        return points

    def plot_data(self):
        self.stop_animation()

        points = self.get_plot_data()
        if len(points) < 2:
            print("Please enter at least two valid data points")
            return

        x_values, y_values = zip(*points)

        self.ax.clear()

        if self.style_dropdown.currentText() == "Connecting Lines":
            self.ax.plot(x_values, y_values, 'bo-')
        elif self.style_dropdown.currentText() == "Smooth Curve":
            num_points = self.points_slider.value()
            x_new = np.linspace(min(x_values), max(x_values), num_points)
            interp_method = self.interp_dropdown.currentText()

            if len(set(x_values)) > 3 or interp_method != 'cubic':
                if len(set(x_values)) == len(x_values):  # No duplicates
                    f = interpolate.interp1d(x_values, y_values, kind=interp_method)
                else:  # Handle duplicates
                    f = interpolate.UnivariateSpline(x_values, y_values, k=min(3, len(set(x_values)) - 1))
                y_smooth = f(x_new)
                self.ax.plot(x_new, y_smooth, 'b-')
            else:
                self.ax.plot(x_values, y_values, 'b-')  # Fallback to simple line if cubic is not possible

            self.ax.plot(x_values, y_values, 'bo')  # Add original points
        elif self.style_dropdown.currentText() == "Polynomial Fit":
            degree = self.poly_degree_spinner.value()
            coeffs = np.polyfit(x_values, y_values, degree)
            p = np.poly1d(coeffs)

            x_new = np.linspace(min(x_values), max(x_values), 100)
            y_new = p(x_new)

            self.ax.plot(x_values, y_values, 'bo', label='Data Points')
            self.ax.plot(x_new, y_new, 'r-', label=f'Polynomial Fit (degree {degree})')
            self.ax.legend()

            # Calculate and display R-squared
            y_pred = p(x_values)
            r_squared = 1 - (np.sum((np.array(y_values) - y_pred) ** 2) / np.sum(
                (np.array(y_values) - np.mean(y_values)) ** 2))
            self.ax.set_title(f'Polynomial Fit (R² = {r_squared:.4f})')

            # Print equation
            eq = f"y = {coeffs[0]:.4f}"
            for i, coeff in enumerate(coeffs[1:], 1):
                eq += f" + {coeff:.4f}x^{degree - i}"
            print(f"Polynomial fit equation: {eq}")
            print(f"R-squared: {r_squared:.4f}")

        self.set_labels()
        self.canvas.draw()

    def set_labels(self):
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

    def animate(self, i):
        points = self.get_plot_data()[:i + 1]
        if len(points) < 2:
            return
        x_values, y_values = zip(*points)

        self.ax.clear()
        if self.style_dropdown.currentText() == "Connecting Lines":
            self.ax.plot(x_values, y_values, 'bo-')
        else:  # Smooth Curve
            if len(set(x_values)) > 3:  # Need at least 4 unique points for cubic interpolation
                if len(set(x_values)) == len(x_values):  # No duplicates
                    f = interpolate.interp1d(x_values, y_values, kind='cubic')
                else:  # Handle duplicates
                    f = interpolate.UnivariateSpline(x_values, y_values, k=min(3, len(set(x_values)) - 1))
                x_new = np.linspace(min(x_values), max(x_values), 300)
                y_smooth = f(x_new)
                self.ax.plot(x_new, y_smooth, 'b-')
            self.ax.plot(x_values, y_values, 'bo')  # Add original points

        self.set_labels()

        # Set consistent axis limits
        all_x, all_y = zip(*self.get_plot_data())
        self.ax.set_xlim(min(all_x), max(all_x))
        self.ax.set_ylim(min(all_y), max(all_y))

    def toggle_animation(self):
        if self.animation is None:
            self.start_animation()
        else:
            self.stop_animation()

    def start_animation(self):
        points = self.get_plot_data()
        if len(points) < 2:
            print("Please enter at least two valid data points")
            return

        self.animation = FuncAnimation(self.figure, self.animate, frames=len(points),
                                       interval=self.animation_speed, repeat=True)
        self.canvas.draw()
        self.animate_button.setText('Stop Animation')

    def stop_animation(self):
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
            self.plot_data()  # Redraw the full plot
            self.animate_button.setText('Animate Plot')

    def update_animation_speed(self, value):
        self.animation_speed = value
        if self.animation:
            self.animation.event_source.interval = self.animation_speed

    def open_best_fit_window(self):
        best_fit_window = BestFitLineWindow(self)
        best_fit_window.exec()


class BestFitLineWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Best Fit Line Analysis")
        self.setGeometry(200, 200, 800, 600)

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left panel for data input and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        layout.addWidget(left_panel)

        # Create table for data entry
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['X', 'Y'])
        left_layout.addWidget(self.table)

        # Create 'Add Row' button
        add_row_button = QPushButton('Add Row')
        add_row_button.clicked.connect(self.add_row)
        left_layout.addWidget(add_row_button)

        # Polynomial degree selection
        degree_layout = QHBoxLayout()
        degree_layout.addWidget(QLabel('Polynomial Degree:'))
        self.degree_spinbox = QSpinBox()
        self.degree_spinbox.setMinimum(1)
        self.degree_spinbox.setMaximum(10)
        self.degree_spinbox.setValue(1)
        degree_layout.addWidget(self.degree_spinbox)
        left_layout.addLayout(degree_layout)

        # Create 'Find Best Fit' button
        fit_button = QPushButton('Find Best Fit')
        fit_button.clicked.connect(self.find_best_fit)
        left_layout.addWidget(fit_button)

        # Right panel for plot display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        layout.addWidget(right_panel)

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

    def get_data(self):
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

        return np.array(x_values), np.array(y_values)

    def find_best_fit(self):
        x, y = self.get_data()
        if len(x) < 2:
            print("Please enter at least two valid data points")
            return

        degree = self.degree_spinbox.value()
        coeffs = np.polyfit(x, y, degree)
        p = np.poly1d(coeffs)

        # Calculate R-squared
        y_pred = p(x)
        r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))

        # Plot
        self.ax.clear()
        self.ax.scatter(x, y, color='blue', label='Data Points')
        x_line = np.linspace(min(x), max(x), 100)
        self.ax.plot(x_line, p(x_line), color='red', label=f'Best Fit (degree {degree})')
        self.ax.legend()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title(f'Best Fit Line (R² = {r_squared:.4f})')
        self.canvas.draw()

        # Print equation
        eq = f"y = {coeffs[0]:.4f}"
        for i, coeff in enumerate(coeffs[1:], 1):
            eq += f" + {coeff:.4f}x^{degree - i}"
        print(f"Best fit equation: {eq}")
        print(f"R-squared: {r_squared:.4f}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotterApp()
    window.show()
    sys.exit(app.exec())