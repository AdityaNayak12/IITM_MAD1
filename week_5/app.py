from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)


class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


COURSE_MAP = {
    'course_1': 1,
    'course_2': 2,
    'course_3': 3,
    'course_4': 4
}


def get_course_id(val):
    if val in COURSE_MAP:
        return COURSE_MAP[val]
    if str(val).isdigit():
        return int(val)
    if '_' in str(val):
        try:
            return int(str(val).split('_')[1])
        except (ValueError, IndexError):
            pass
    return None


@app.route('/', methods=['GET'])
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'GET':
        return render_template('create.html')

    if request.method == 'POST':
        roll = request.form.get('roll')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        courses = request.form.getlist('courses')

        existing_student = Student.query.filter_by(roll_number=roll).first()
        if existing_student:
            return render_template('already_exists.html')

        student = Student(roll_number=roll, first_name=f_name, last_name=l_name)
        db.session.add(student)
        db.session.flush()

        for c in courses:
            cid = get_course_id(c)
            if cid is not None:
                enrollment = Enrollments(estudent_id=student.student_id, ecourse_id=cid)
                db.session.add(enrollment)

        db.session.commit()
        return redirect('/')


@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return redirect('/')

    if request.method == 'GET':
        enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
        enrolled_course_ids = [e.ecourse_id for e in enrollments]
        return render_template('update.html', student=student, enrolled_course_ids=enrolled_course_ids)

    if request.method == 'POST':
        student.first_name = request.form.get('f_name')
        student.last_name = request.form.get('l_name')

        Enrollments.query.filter_by(estudent_id=student_id).delete()
        courses = request.form.getlist('courses')

        for c in courses:
            cid = get_course_id(c)
            if cid is not None:
                enrollment = Enrollments(estudent_id=student_id, ecourse_id=cid)
                db.session.add(enrollment)

        db.session.commit()
        return redirect('/')


@app.route('/student/<int:student_id>/delete', methods=['GET'])
def delete_student(student_id):
    Enrollments.query.filter_by(estudent_id=student_id).delete()
    Student.query.filter_by(student_id=student_id).delete()
    db.session.commit()
    return redirect('/')


@app.route('/student/<int:student_id>', methods=['GET'])
def student_details(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return redirect('/')

    courses = db.session.query(Course).join(
        Enrollments, Enrollments.ecourse_id == Course.course_id
    ).filter(Enrollments.estudent_id == student_id).all()

    return render_template('details.html', student=student, courses=courses)


if __name__ == '__main__':
    app.run()
