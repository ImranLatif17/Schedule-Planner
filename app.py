import sys
import csv, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QDateTimeEdit, QDateEdit, QTableWidget, QTableWidgetItem
)
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

shifts = []


# --- chart widget ---
class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 2))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def update_chart(self, work_hours, study_hours):
        self.ax.clear()
        labels = ['Work', 'Study']
        values = [work_hours, study_hours]
        bars = self.ax.bar(labels, values, color=['#4CAF50', '#2196F3'])
        self.ax.set_ylabel("Hours")
        self.ax.set_title("Work vs Study Hours")
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2, height + 0.1, str(height),
                         ha='center', va='bottom', color='white' if height > 0 else 'black')
        self.fig.tight_layout()
        self.draw()


class ShiftPlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shift & Study Planner")
        self.setGeometry(200, 200, 850, 550)

        # main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- input row (add/delete) ---
        input_row = QHBoxLayout()
        self.type_box = QComboBox()
        self.type_box.addItems(["Work", "Study"])

        self.start_input = QDateTimeEdit()
        self.start_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_input.setCalendarPopup(True)
        self.start_input.setDateTime(datetime.now())

        self.end_input = QDateTimeEdit()
        self.end_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_input.setCalendarPopup(True)
        self.end_input.setDateTime(datetime.now())

        add_btn = QPushButton("Add Shift")
        add_btn.clicked.connect(self.add_shift)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_shift)

        input_row.addWidget(self.type_box)
        input_row.addWidget(self.start_input)
        input_row.addWidget(self.end_input)
        input_row.addWidget(add_btn)
        input_row.addWidget(delete_btn)
        layout.addLayout(input_row)

        # --- filter row ---
        filter_row = QHBoxLayout()

        filter_label = QLabel("Filter:")
        self.filter_box = QComboBox()
        self.filter_box.addItems(["All", "Work", "Study"])
        self.filter_box.currentTextChanged.connect(lambda: self.update_table())

        date_label = QLabel("From:")
        self.start_filter = QDateEdit()
        self.start_filter.setDisplayFormat("yyyy-MM-dd")
        self.start_filter.setCalendarPopup(True)
        self.start_filter.setDate(datetime.now().date())

        end_label = QLabel("To:")
        self.end_filter = QDateEdit()
        self.end_filter.setDisplayFormat("yyyy-MM-dd")
        self.end_filter.setCalendarPopup(True)
        self.end_filter.setDate(datetime.now().date())

        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.update_table)

        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.filter_box)
        filter_row.addWidget(date_label)
        filter_row.addWidget(self.start_filter)
        filter_row.addWidget(end_label)
        filter_row.addWidget(self.end_filter)
        filter_row.addWidget(apply_filter_btn)
        layout.addLayout(filter_row)

        # --- chart ---
        self.chart = ChartCanvas(self)
        layout.addWidget(self.chart)

        # --- table ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Type", "Start", "End", "Duration"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        layout.addWidget(self.table)

        # --- summary ---
        self.summary_label = QLabel("Total Work Hours: 0 | Total Study Hours: 0")
        layout.addWidget(self.summary_label)

        # --- theme toggle ---
        self.theme = "light"
        theme_btn = QPushButton("Switch to Dark Mode")
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)

        self.setLayout(layout)
        self.load_shifts()

    # --- CSV handling ---
    def save_shifts(self):
        with open("shifts.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Start", "End", "Duration"])
            for s in shifts:
                writer.writerow([
                    s["type"],
                    s["start"].strftime("%Y-%m-%d %H:%M"),
                    s["end"].strftime("%Y-%m-%d %H:%M"),
                    s["duration"]
                ])

    def load_shifts(self):
        if not os.path.exists("shifts.csv") or os.path.getsize("shifts.csv") == 0:
            return
        with open("shifts.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not all(k in row for k in ("Type", "Start", "End", "Duration")):
                    continue
                shifts.append({
                    "type": row["Type"],
                    "start": datetime.strptime(row["Start"], "%Y-%m-%d %H:%M"),
                    "end": datetime.strptime(row["End"], "%Y-%m-%d %H:%M"),
                    "duration": int(row["Duration"])
                })
        self.update_table()
        self.update_summary()

    # --- add/delete ---
    def add_shift(self):
        try:
            shift_type = self.type_box.currentText()
            start = self.start_input.dateTime().toPyDateTime()
            end = self.end_input.dateTime().toPyDateTime()
            duration = int((end - start).seconds / 3600)
            shifts.append({
                "type": shift_type,
                "start": start,
                "end": end,
                "duration": duration
            })
            self.update_table()
            self.update_summary()
            self.save_shifts()
        except Exception:
            self.summary_label.setText("⚠️ Invalid input! Please check your dates.")

    def delete_shift(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            if 0 <= r < len(shifts):
                shifts.pop(r)
        self.update_table()
        self.update_summary()
        self.save_shifts()

    # --- table + summary updates ---
    def update_table(self):
        filter_type = self.filter_box.currentText() if hasattr(self, "filter_box") else "All"
        start_date = self.start_filter.date().toPyDate() if hasattr(self, "start_filter") else None
        end_date = self.end_filter.date().toPyDate() if hasattr(self, "end_filter") else None

        filtered_shifts = []
        for s in shifts:
            if filter_type != "All" and s["type"] != filter_type:
                continue
            if start_date and s["start"].date() < start_date:
                continue
            if end_date and s["end"].date() > end_date:
                continue
            filtered_shifts.append(s)

        self.table.setRowCount(len(filtered_shifts))
        for i, s in enumerate(filtered_shifts):
            self.table.setItem(i, 0, QTableWidgetItem(s["type"]))
            self.table.setItem(i, 1, QTableWidgetItem(s["start"].strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(i, 2, QTableWidgetItem(s["end"].strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(i, 3, QTableWidgetItem(str(s["duration"])))

        self.update_summary()

    def update_summary(self):
        work_hours = sum(s["duration"] for s in shifts if s["type"] == "Work")
        study_hours = sum(s["duration"] for s in shifts if s["type"] == "Study")
        self.summary_label.setText(
            f"Total Work Hours: {work_hours} | Total Study Hours: {study_hours}"
        )
        if hasattr(self, "chart"):
            self.chart.update_chart(work_hours, study_hours)

    # --- theme toggle ---
    def toggle_theme(self):
        if self.theme == "light":
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: Segoe UI;
                    font-size: 10pt;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QComboBox, QDateTimeEdit, QDateEdit, QTableWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #555;
                }
                QHeaderView::section {
                    background-color: #444;
                    color: #fff;
                }
            """)
            self.theme = "dark"
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                    color: #000000;
                    font-family: Segoe UI;
                    font-size: 10pt;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 1px solid #aaa;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QComboBox, QDateTimeEdit, QDateEdit, QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                }
                QHeaderView::section {
                    background-color: #ddd;
                    color: #000;
                }
            """)
            self.theme = "light"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShiftPlanner()
    window.show()
    sys.exit(app.exec_())
