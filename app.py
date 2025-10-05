import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QDateTimeEdit, QTableWidget, QTableWidgetItem
)
from datetime import datetime

shifts = []


class ShiftPlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shift & Study Planner")
        self.setGeometry(200, 200, 700, 450)

        # main layout
        layout = QVBoxLayout()

        # --- input row ---
        input_row = QHBoxLayout()
        self.type_box = QComboBox()
        self.type_box.addItems(["Work", "Study"])

        self.start_input = QDateTimeEdit()
        self.start_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_input.setCalendarPopup(True)

        self.end_input = QDateTimeEdit()
        self.end_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_input.setCalendarPopup(True)

        add_btn = QPushButton("Add Shift")
        add_btn.clicked.connect(self.add_shift)

        input_row.addWidget(self.type_box)
        input_row.addWidget(self.start_input)
        input_row.addWidget(self.end_input)
        input_row.addWidget(add_btn)

        layout.addLayout(input_row)

        # --- table ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Type", "Start", "End", "Duration"])
        layout.addWidget(self.table)

        # --- summary ---
        self.summary_label = QLabel("Total Work Hours: 0 | Total Study Hours: 0")
        layout.addWidget(self.summary_label)

        self.setLayout(layout)

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
        except Exception:
            self.summary_label.setText("⚠️ Invalid input! Please check your dates.")

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
        self.summary_label.setText(
            f"Total Work Hours: {work_hours} | Total Study Hours: {study_hours}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShiftPlanner()
    window.show()
    sys.exit(app.exec_())
