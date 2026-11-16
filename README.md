# IITM BS Degree - Modern Application Development I (BSCCS2003)

Repository containing coursework and lab assignments for Modern Application Development I (MAD-1).

## Week 2: HTML Lab Assignment
- `index.html` - Home page (Student data)
- `academics.html` - Academics page (Marksheet table)
- `personal.html` - Personal page (Degree overview with images)
- `contact.html` - Contact page (Office details & address)
- `resume.html` - Resume page (Link to CV download)
- `25f3005502.zip` - Packaged submission archive containing all required files

## Week 3: Python CLI & Jinja2 Lab Assignment
- `app.py` - Single Python CLI script for student/course marks reporting and HTML generation
- `data.csv` - Student marks dataset
- `25f3005502.zip` - Packaged submission archive containing `app.py` (only)

## Week 4: Flask Web Application Lab Assignment
- `app.py` - Flask web application handling student and course marks queries
- `templates/` - HTML5 templates (`index.html`, `student_details.html`, `course_details.html`, `error.html`)
- `static/` - Static assets directory including generated `histogram.png`
- `25f3005502.zip` - Packaged submission archive containing `app.py`, `templates/`, and `static/`

## Week 5: Flask & SQLite Lab Assignment
- `app.py` - Flask application with SQLAlchemy models (`Student`, `Course`, `Enrollments`) for CRUD operations
- `templates/` - Jinja2 templates for listing, creating, updating, and deleting records
- `database.sqlite3` - SQLite database containing student and course data
- `25f3005502.zip` - Packaged submission archive containing `app.py` and `templates/`

## Week 6: Flask-RESTful API Lab Assignment
- `app.py` - RESTful API service implemented with Flask-RESTful and Flask-SQLAlchemy
- `openapi_week6.yaml` - OpenAPI specification covering Course, Student, and Enrollment resources
- `api_database.sqlite3` - SQLite database initialized with schemas for `course`, `student`, and `enrollment`
- `test_app.py` - Automated test suite verifying endpoints, schemas, status codes, and error codes
- `25f3005502.zip` - Packaged submission archive containing `app.py`
