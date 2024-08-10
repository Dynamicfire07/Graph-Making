import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QCheckBox, QMenuBar, QMenu, QFileDialog, QInputDialog, QComboBox,
                             QSlider)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import matplotlib
import re
import numpy as np
from scipy import interpolate


class PlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Line Plotter")
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
        self.points_slider.setMaximum(1000)
        self.points_slider.setValue(500)
        self.points_slider.setTickInterval(100)
        self.points_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        points_layout.addWidget(self.points_slider)
        left_layout.addLayout(points_layout)

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

        return sorted(zip(x_values, y_values))

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
        else:  # Smooth Curve
            num_points = self.points_slider.value()
            x_new = np.linspace(min(x_values), max(x_values), num_points)
            interp_method = self.interp_dropdown.currentText()

            if len(x_values) > 3 or interp_method != 'cubic':
                f = interpolate.interp1d(x_values, y_values, kind=interp_method)
                y_smooth = f(x_new)
                self.ax.plot(x_new, y_smooth, 'b-')
            else:
                self.ax.plot(x_values, y_values, 'b-')  # Fallback to simple line if cubic is not possible

            self.ax.plot(x_values, y_values, 'bo')  # Add original points

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

    def animate(self, frame):
        points = self.get_plot_data()
        if len(points) < 2:
            return

        x_values, y_values = zip(*points)

        # Calculate the current progress
        self.animation_progress += 0.02
        if self.animation_progress > 1:
            self.animation_progress = 0

        # Interpolate between points
        t = np.linspace(0, 1, len(points))
        t_current = np.linspace(0, self.animation_progress, 100)

        x_interp = np.interp(t_current, t, x_values)
        y_interp = np.interp(t_current, t, y_values)

        self.ax.clear()
        if self.style_dropdown.currentText() == "Connecting Lines":
            self.ax.plot(x_interp, y_interp, 'bo-')
        else:  # Smooth Curve
            if len(x_interp) > 3:  # Need at least 4 points for cubic interpolation
                f = interpolate.interp1d(x_interp, y_interp, kind='cubic')
                x_smooth = np.linspace(min(x_interp), max(x_interp), 300)
                y_smooth = f(x_smooth)
                self.ax.plot(x_smooth, y_smooth, 'b-')
            self.ax.plot(x_interp, y_interp, 'bo')  # Add interpolated points

        self.set_labels()

        # Set consistent axis limits
        self.ax.set_xlim(min(x_values), max(x_values))
        self.ax.set_ylim(min(y_values), max(y_values))

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

        self.animation_progress = 0
        self.animation = FuncAnimation(self.figure, self.animate, frames=None,
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
        self.animation_speed = 210 - value  # Invert the slider value for more intuitive control
        if self.animation:
            self.animation.event_source.interval = self.animation_speed


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotterApp()
    window.show()
    sys.exit(app.exec())