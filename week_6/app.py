import json
from flask import Flask, make_response, request
from flask_restful import Api, Resource, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)


# ---------------------------------------------------------
# Database Models
# ---------------------------------------------------------

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_description = db.Column(db.String)


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


# ---------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)
        self.response.headers["Content-Type"] = "application/json"


class NotFoundError(HTTPException):
    def __init__(self, status_code=404):
        self.response = make_response('', status_code)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def get_request_data():
    if request.is_json:
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            return data
    data = request.get_json(force=True, silent=True)
    if isinstance(data, dict):
        return data
    if request.form:
        return request.form.to_dict()
    if request.args:
        return request.args.to_dict()
    return {}


# ---------------------------------------------------------
# Response Marshalling Fields
# ---------------------------------------------------------

course_fields = {
    'course_id': fields.Integer,
    'course_name': fields.String,
    'course_code': fields.String,
    'course_description': fields.String
}

student_fields = {
    'student_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'roll_number': fields.String
}

enrollment_fields = {
    'enrollment_id': fields.Integer,
    'student_id': fields.Integer,
    'course_id': fields.Integer
}


# ---------------------------------------------------------
# Resources
# ---------------------------------------------------------

class CourseAPI(Resource):
    @marshal_with(course_fields)
    def get(self, course_id=None):
        if course_id is None:
            raise NotFoundError(404)
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            raise NotFoundError(404)
        return course, 200

    @marshal_with(course_fields)
    def put(self, course_id=None):
        if course_id is None:
            raise NotFoundError(404)
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            raise NotFoundError(404)

        data = get_request_data()
        course_name = data.get('course_name')
        course_code = data.get('course_code')
        course_description = data.get('course_description')

        if course_name is None or str(course_name).strip() == '':
            raise BusinessValidationError(400, "COURSE001", "Course Name is required")
        if course_code is None or str(course_code).strip() == '':
            raise BusinessValidationError(400, "COURSE002", "Course Code is required")

        existing = Course.query.filter(Course.course_code == course_code, Course.course_id != course_id).first()
        if existing:
            raise NotFoundError(409)

        course.course_name = course_name
        course.course_code = course_code
        if 'course_description' in data:
            course.course_description = course_description

        db.session.commit()
        return course, 200

    def delete(self, course_id=None):
        if course_id is None:
            raise NotFoundError(404)
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            raise NotFoundError(404)

        Enrollment.query.filter_by(course_id=course_id).delete()
        db.session.delete(course)
        db.session.commit()
        return "", 200

    @marshal_with(course_fields)
    def post(self, course_id=None):
        if course_id is not None:
            raise NotFoundError(404)

        data = get_request_data()
        course_name = data.get('course_name')
        course_code = data.get('course_code')
        course_description = data.get('course_description')

        if course_name is None or str(course_name).strip() == '':
            raise BusinessValidationError(400, "COURSE001", "Course Name is required")
        if course_code is None or str(course_code).strip() == '':
            raise BusinessValidationError(400, "COURSE002", "Course Code is required")

        existing = Course.query.filter_by(course_code=course_code).first()
        if existing:
            raise NotFoundError(409)

        new_course = Course(
            course_name=course_name,
            course_code=course_code,
            course_description=course_description
        )
        db.session.add(new_course)
        db.session.commit()
        return new_course, 201


class StudentAPI(Resource):
    @marshal_with(student_fields)
    def get(self, student_id=None):
        if student_id is None:
            raise NotFoundError(404)
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            raise NotFoundError(404)
        return student, 200

    @marshal_with(student_fields)
    def put(self, student_id=None):
        if student_id is None:
            raise NotFoundError(404)
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            raise NotFoundError(404)

        data = get_request_data()
        roll_number = data.get('roll_number')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if roll_number is None or str(roll_number).strip() == '':
            raise BusinessValidationError(400, "STUDENT001", "Roll Number required")
        if first_name is None or str(first_name).strip() == '':
            raise BusinessValidationError(400, "STUDENT002", "First Name is required")

        existing = Student.query.filter(Student.roll_number == roll_number, Student.student_id != student_id).first()
        if existing:
            raise NotFoundError(409)

        student.roll_number = roll_number
        student.first_name = first_name
        if 'last_name' in data:
            student.last_name = last_name

        db.session.commit()
        return student, 200

    def delete(self, student_id=None):
        if student_id is None:
            raise NotFoundError(404)
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            raise NotFoundError(404)

        Enrollment.query.filter_by(student_id=student_id).delete()
        db.session.delete(student)
        db.session.commit()
        return "", 200

    @marshal_with(student_fields)
    def post(self, student_id=None):
        if student_id is not None:
            raise NotFoundError(404)

        data = get_request_data()
        roll_number = data.get('roll_number')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if roll_number is None or str(roll_number).strip() == '':
            raise BusinessValidationError(400, "STUDENT001", "Roll Number required")
        if first_name is None or str(first_name).strip() == '':
            raise BusinessValidationError(400, "STUDENT002", "First Name is required")

        existing = Student.query.filter_by(roll_number=roll_number).first()
        if existing:
            raise NotFoundError(409)

        new_student = Student(
            roll_number=roll_number,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(new_student)
        db.session.commit()
        return new_student, 201


class EnrollmentAPI(Resource):
    @marshal_with(enrollment_fields)
    def get(self, student_id, course_id=None):
        if course_id is not None:
            raise NotFoundError(404)
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            raise BusinessValidationError(400, "ENROLLMENT002", "Student does not exist.")

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        if not enrollments:
            raise NotFoundError(404)
        return enrollments, 200

    @marshal_with(enrollment_fields)
    def post(self, student_id, course_id=None):
        if course_id is not None:
            raise NotFoundError(404)
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            raise NotFoundError(404)

        data = get_request_data()
        cid = data.get('course_id')
        if cid is None:
            raise BusinessValidationError(400, "ENROLLMENT001", "Course does not exist")
        try:
            cid_int = int(cid)
        except (ValueError, TypeError):
            raise BusinessValidationError(400, "ENROLLMENT001", "Course does not exist")

        course = Course.query.filter_by(course_id=cid_int).first()
        if not course:
            raise BusinessValidationError(400, "ENROLLMENT001", "Course does not exist")

        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=cid_int).first()
        if not enrollment:
            enrollment = Enrollment(student_id=student_id, course_id=cid_int)
            db.session.add(enrollment)
            db.session.commit()

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        return enrollments, 201

    def delete(self, student_id, course_id=None):
        if course_id is None:
            raise NotFoundError(404)
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            raise BusinessValidationError(400, "ENROLLMENT002", "Student does not exist.")

        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            raise BusinessValidationError(400, "ENROLLMENT001", "Course does not exist")

        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            raise NotFoundError(404)

        db.session.delete(enrollment)
        db.session.commit()
        return "", 200


# ---------------------------------------------------------
# API Routing
# ---------------------------------------------------------

api.add_resource(CourseAPI, '/api/course', '/api/course/<int:course_id>')
api.add_resource(StudentAPI, '/api/student', '/api/student/<int:student_id>')
api.add_resource(EnrollmentAPI, '/api/student/<int:student_id>/course', '/api/student/<int:student_id>/course/<int:course_id>')


if __name__ == '__main__':
    app.run()
