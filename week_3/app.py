import sys
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from jinja2 import Template

# HTML Templates

STUDENT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Data</title>
</head>
<body>
    <h1>Student Details</h1>
    <table border="1" id="student-details-table">
        <tr>
            <th>Student id</th>
            <th>Course id</th>
            <th>Marks</th>
        </tr>
        {% for row in records %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
        </tr>
        {% endfor %}
        <tr>
            <td colspan="2" style="text-align: center;">Total Marks</td>
            <td>{{ total_marks }}</td>
        </tr>
    </table>
</body>
</html>"""

COURSE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Course Data</title>
</head>
<body>
    <h1>Course Details</h1>
    <table border="1" id="course-details-table">
        <tr>
            <th>Average Marks</th>
            <th>Maximum Marks</th>
        </tr>
        <tr>
            <td>{{ avg_marks }}</td>
            <td>{{ max_marks }}</td>
        </tr>
    </table>
    <img src="histogram.png" alt="Course Histogram">
</body>
</html>"""

ERROR_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Something Went Wrong</title>
</head>
<body>
    <h1>Wrong Inputs</h1>
    <p>Something went wrong</p>
</body>
</html>"""


def render_html(template_str, **context):
    template = Template(template_str)
    rendered_content = template.render(**context)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(rendered_content)


def load_data():
    try:
        with open("data.csv", mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header row
            if header is None:
                return None
            records = []
            for row in reader:
                if row:
                    cleaned_row = [col.strip() for col in row]
                    if len(cleaned_row) >= 3:
                        records.append(cleaned_row)
            return records
    except Exception:
        return None


def main():
    # Validate command line arguments count
    if len(sys.argv) != 3:
        render_html(ERROR_TEMPLATE)
        return

    flag = sys.argv[1].strip()
    target_id = sys.argv[2].strip()

    if flag not in ("-s", "-c"):
        render_html(ERROR_TEMPLATE)
        return

    data = load_data()
    if data is None:
        render_html(ERROR_TEMPLATE)
        return

    # Student Details
    if flag == "-s":
        student_records = [row for row in data if row[0] == target_id]
        if not student_records:
            render_html(ERROR_TEMPLATE)
            return

        try:
            total_marks = sum(int(row[2]) for row in student_records)
        except ValueError:
            render_html(ERROR_TEMPLATE)
            return

        render_html(STUDENT_TEMPLATE, records=student_records, total_marks=total_marks)

    # Course Details
    elif flag == "-c":
        course_records = [row for row in data if row[1] == target_id]
        if not course_records:
            render_html(ERROR_TEMPLATE)
            return

        try:
            marks = [int(row[2]) for row in course_records]
        except ValueError:
            render_html(ERROR_TEMPLATE)
            return

        avg_marks = sum(marks) / len(marks)
        max_marks = max(marks)

        # Generate Histogram Plot
        plt.figure()
        plt.hist(marks)
        plt.xlabel("Marks")
        plt.ylabel("Frequency")
        plt.savefig("histogram.png")
        plt.close()

        render_html(COURSE_TEMPLATE, avg_marks=avg_marks, max_marks=max_marks)


if __name__ == "__main__":
    main()
