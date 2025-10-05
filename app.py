import sys
import csv, os
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

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_shift)

        input_row.addWidget(self.type_box)
        input_row.addWidget(self.start_input)
        input_row.addWidget(self.end_input)
        input_row.addWidget(add_btn)
        input_row.addWidget(delete_btn)
        layout.addLayout(input_row)

        # --- table ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Type", "Start", "End", "Duration"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        layout.addWidget(self.table)

        # --- summary ---
        self.summary_label = QLabel("Total Work Hours: 0 | Total Study Hours: 0")
        layout.addWidget(self.summary_label)

        self.setLayout(layout)

        # load saved shifts from csv when starting
        self.load_shifts()

    # save all shifts to csv
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

    # load shifts from csv if exists
    def load_shifts(self):
        # skip if file doesn't exist or is empty
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
            self.save_shifts()  # save after every new shift
        except Exception:
            self.summary_label.setText("⚠️ Invalid input! Please check your dates.")

    def delete_shift(self):
        # get the selected rows
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)

        # remove them from shifts list
        for r in rows:
            if 0 <= r < len(shifts):
                shifts.pop(r)

        # refresh UI and save to CSV
        self.update_table()
        self.update_summary()
        self.save_shifts()

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
