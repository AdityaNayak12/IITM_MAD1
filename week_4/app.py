import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)


def load_data():
    try:
        with open("data.csv", mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                return None
            records = []
            for row in reader:
                if row:
                    cleaned_row = [col.strip() for col in row]
                    if len(cleaned_row) >= 3 and any(cleaned_row):
                        records.append(cleaned_row)
            return records
    except Exception:
        return None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        id_type = request.form.get("ID")
        id_value = request.form.get("id_value")

        if not id_type or id_value is None or not id_value.strip():
            return render_template("error.html")

        id_value = id_value.strip()
        records = load_data()

        if records is None:
            return render_template("error.html")

        if id_type == "student_id":
            student_records = [r for r in records if r[0] == id_value]
            if not student_records:
                return render_template("error.html")

            try:
                total_marks = sum(int(r[2]) for r in student_records)
            except (ValueError, TypeError):
                return render_template("error.html")

            return render_template(
                "student_details.html",
                records=student_records,
                data=student_records,
                total_marks=total_marks,
                Total_Marks=total_marks
            )

        elif id_type == "course_id":
            course_records = [r for r in records if r[1] == id_value]
            if not course_records:
                return render_template("error.html")

            try:
                marks = [int(r[2]) for r in course_records]
            except (ValueError, TypeError):
                return render_template("error.html")

            avg_marks = sum(marks) / len(marks)
            max_marks = max(marks)

            os.makedirs("static", exist_ok=True)
            plt.figure()
            plt.hist(marks)
            plt.xlabel("Marks")
            plt.ylabel("Frequency")
            plt.savefig(os.path.join("static", "histogram.png"))
            plt.close()

            return render_template(
                "course_details.html",
                avg_marks=avg_marks,
                max_marks=max_marks,
                Marks={"avg": avg_marks, "max": max_marks}
            )

        else:
            return render_template("error.html")


if __name__ == "__main__":
    app.run()
