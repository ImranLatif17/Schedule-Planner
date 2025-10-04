import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem
from datetime import datetime

shifts = []

class ShiftPlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shift & Study Planner")
        self.setGeometry(200, 200, 700, 450)

        # Main layout
        layout = QVBoxLayout()

        # --- Input row ---
        input_row = QHBoxLayout()
        self.type_box = QComboBox()
        self.type_box.addItems(["Work", "Study"])

        self.start_input = QLineEdit("YYYY-MM-DD HH:MM")
        self.end_input = QLineEdit("YYYY-MM-DD HH:MM")

        add_btn = QPushButton("Add Shift")
        add_btn.clicked.connect(self.add_shift)

        input_row.addWidget(self.type_box)
        input_row.addWidget(self.start_input)
        input_row.addWidget(self.end_input)
        input_row.addWidget(add_btn)

        layout.addLayout(input_row)

        # --- Table ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Type", "Start", "End", "Duration"])
        layout.addWidget(self.table)

        # --- Summary ---
        self.summary_label = QLabel("Total Work Hours: 0 | Total Study Hours: 0")
        layout.addWidget(self.summary_label)

        self.setLayout(layout)

    def add_shift(self):
        try:
            shift_type = self.type_box.currentText()
            start = datetime.strptime(self.start_input.text(), "%Y-%m-%d %H:%M")
            end = datetime.strptime(self.end_input.text(), "%Y-%m-%d %H:%M")
            duration = int((end - start).seconds / 3600)

            shifts.append({"type": shift_type, "start": start, "end": end, "duration": duration})
            self.update_table()
            self.update_summary()
        except Exception:
            self.summary_label.setText("⚠️ Invalid input! Use YYYY-MM-DD HH:MM")

    def update_table(self):
        self.table.setRowCount(len(shifts))
        for i, s in enumerate(shifts):
            self.table.setItem(i, 0, QTableWidgetItem(s["type"]))
            self.table.setItem(i, 1, QTableWidgetItem(s["start"].strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(i, 2, QTableWidgetItem(s["end"].strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(i, 3, QTableWidgetItem(str(s["duration"])))

    def update_summary(self):
        work_hours = sum(s["duration"] for s in shifts if s["type"] == "Work")
        study_hours = sum(s["duration"] for s in shifts if s["type"] == "Study")
        self.summary_label.setText(f"Total Work Hours: {work_hours} | Total Study Hours: {study_hours}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShiftPlanner()
    window.show()
    sys.exit(app.exec_())
