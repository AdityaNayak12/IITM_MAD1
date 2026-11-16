import os
import pytest
from app import app, db, Course, Student, Enrollment

@pytest.fixture
def client():
    # Use in-memory SQLite database or temp file for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.drop_all()

# =========================================================
# Course API Tests
# =========================================================

def test_course_create_success(client):
    res = client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": "MA101",
        "course_description": "Course Description Example"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["course_id"] == 1
    assert data["course_name"] == "Maths1"
    assert data["course_code"] == "MA101"
    assert data["course_description"] == "Course Description Example"

def test_course_create_missing_name(client):
    res = client.post('/api/course', json={
        "course_code": "MA101"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "COURSE001"
    assert data["error_message"] == "Course Name is required"

def test_course_create_empty_name(client):
    res = client.post('/api/course', json={
        "course_name": "   ",
        "course_code": "MA101"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "COURSE001"
    assert data["error_message"] == "Course Name is required"

def test_course_create_missing_code(client):
    res = client.post('/api/course', json={
        "course_name": "Maths1"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "COURSE002"
    assert data["error_message"] == "Course Code is required"

def test_course_create_empty_code(client):
    res = client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": ""
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "COURSE002"
    assert data["error_message"] == "Course Code is required"

def test_course_create_duplicate_code(client):
    client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": "MA101"
    })
    res = client.post('/api/course', json={
        "course_name": "Maths2",
        "course_code": "MA101"
    })
    assert res.status_code == 409

def test_course_get_success(client):
    post_res = client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": "MA101"
    })
    cid = post_res.get_json()["course_id"]

    res = client.get(f'/api/course/{cid}')
    assert res.status_code == 200
    data = res.get_json()
    assert data["course_id"] == cid
    assert data["course_name"] == "Maths1"
    assert data["course_code"] == "MA101"

def test_course_get_not_found(client):
    res = client.get('/api/course/999')
    assert res.status_code == 404

def test_course_update_success(client):
    post_res = client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": "MA101"
    })
    cid = post_res.get_json()["course_id"]

    res = client.put(f'/api/course/{cid}', json={
        "course_name": "Maths Advanced",
        "course_code": "MA102",
        "course_description": "Advanced Maths"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["course_id"] == cid
    assert data["course_name"] == "Maths Advanced"
    assert data["course_code"] == "MA102"
    assert data["course_description"] == "Advanced Maths"

def test_course_update_not_found(client):
    res = client.put('/api/course/999', json={
        "course_name": "Maths",
        "course_code": "MA101"
    })
    assert res.status_code == 404

def test_course_update_missing_name(client):
    post_res = client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": "MA101"
    })
    cid = post_res.get_json()["course_id"]

    res = client.put(f'/api/course/{cid}', json={
        "course_code": "MA101"
    })
    assert res.status_code == 400
    assert res.get_json()["error_code"] == "COURSE001"

def test_course_update_missing_code(client):
    post_res = client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": "MA101"
    })
    cid = post_res.get_json()["course_id"]

    res = client.put(f'/api/course/{cid}', json={
        "course_name": "Maths1"
    })
    assert res.status_code == 400
    assert res.get_json()["error_code"] == "COURSE002"

def test_course_update_duplicate_code(client):
    client.post('/api/course', json={"course_name": "C1", "course_code": "CODE1"})
    p2 = client.post('/api/course', json={"course_name": "C2", "course_code": "CODE2"})
    cid2 = p2.get_json()["course_id"]

    res = client.put(f'/api/course/{cid2}', json={"course_name": "C2", "course_code": "CODE1"})
    assert res.status_code == 409

def test_course_delete_success(client):
    post_res = client.post('/api/course', json={
        "course_name": "Maths1",
        "course_code": "MA101"
    })
    cid = post_res.get_json()["course_id"]

    res = client.delete(f'/api/course/{cid}')
    assert res.status_code == 200

    get_res = client.get(f'/api/course/{cid}')
    assert get_res.status_code == 404

def test_course_delete_not_found(client):
    res = client.delete('/api/course/999')
    assert res.status_code == 404


# =========================================================
# Student API Tests
# =========================================================

def test_student_create_success(client):
    res = client.post('/api/student', json={
        "first_name": "Narendra",
        "last_name": "Mishra",
        "roll_number": "MA19M010"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["student_id"] == 1
    assert data["first_name"] == "Narendra"
    assert data["last_name"] == "Mishra"
    assert data["roll_number"] == "MA19M010"

def test_student_create_missing_roll(client):
    res = client.post('/api/student', json={
        "first_name": "Narendra",
        "last_name": "Mishra"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "STUDENT001"
    assert data["error_message"] == "Roll Number required"

def test_student_create_empty_roll(client):
    res = client.post('/api/student', json={
        "first_name": "Narendra",
        "roll_number": "   "
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "STUDENT001"
    assert data["error_message"] == "Roll Number required"

def test_student_create_missing_first_name(client):
    res = client.post('/api/student', json={
        "roll_number": "MA19M010"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "STUDENT002"
    assert data["error_message"] == "First Name is required"

def test_student_create_empty_first_name(client):
    res = client.post('/api/student', json={
        "first_name": "",
        "roll_number": "MA19M010"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "STUDENT002"
    assert data["error_message"] == "First Name is required"

def test_student_create_duplicate_roll(client):
    client.post('/api/student', json={
        "first_name": "Narendra",
        "roll_number": "MA19M010"
    })
    res = client.post('/api/student', json={
        "first_name": "Rahul",
        "roll_number": "MA19M010"
    })
    assert res.status_code == 409

def test_student_get_success(client):
    p = client.post('/api/student', json={
        "first_name": "Narendra",
        "last_name": "Mishra",
        "roll_number": "MA19M010"
    })
    sid = p.get_json()["student_id"]

    res = client.get(f'/api/student/{sid}')
    assert res.status_code == 200
    data = res.get_json()
    assert data["student_id"] == sid
    assert data["first_name"] == "Narendra"
    assert data["last_name"] == "Mishra"
    assert data["roll_number"] == "MA19M010"

def test_student_get_not_found(client):
    res = client.get('/api/student/999')
    assert res.status_code == 404

def test_student_update_success(client):
    p = client.post('/api/student', json={
        "first_name": "Narendra",
        "last_name": "Mishra",
        "roll_number": "MA19M010"
    })
    sid = p.get_json()["student_id"]

    res = client.put(f'/api/student/{sid}', json={
        "first_name": "Narendra Kumar",
        "last_name": "Mishra",
        "roll_number": "MA19M011"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["first_name"] == "Narendra Kumar"
    assert data["roll_number"] == "MA19M011"

def test_student_update_not_found(client):
    res = client.put('/api/student/999', json={
        "first_name": "Test",
        "roll_number": "TEST01"
    })
    assert res.status_code == 404

def test_student_update_missing_roll(client):
    p = client.post('/api/student', json={
        "first_name": "Narendra",
        "roll_number": "MA19M010"
    })
    sid = p.get_json()["student_id"]

    res = client.put(f'/api/student/{sid}', json={
        "first_name": "Narendra"
    })
    assert res.status_code == 400
    assert res.get_json()["error_code"] == "STUDENT001"

def test_student_update_missing_first_name(client):
    p = client.post('/api/student', json={
        "first_name": "Narendra",
        "roll_number": "MA19M010"
    })
    sid = p.get_json()["student_id"]

    res = client.put(f'/api/student/{sid}', json={
        "roll_number": "MA19M010"
    })
    assert res.status_code == 400
    assert res.get_json()["error_code"] == "STUDENT002"

def test_student_update_duplicate_roll(client):
    client.post('/api/student', json={"first_name": "S1", "roll_number": "ROLL1"})
    p2 = client.post('/api/student', json={"first_name": "S2", "roll_number": "ROLL2"})
    sid2 = p2.get_json()["student_id"]

    res = client.put(f'/api/student/{sid2}', json={"first_name": "S2", "roll_number": "ROLL1"})
    assert res.status_code == 409

def test_student_delete_success(client):
    p = client.post('/api/student', json={
        "first_name": "Narendra",
        "roll_number": "MA19M010"
    })
    sid = p.get_json()["student_id"]

    res = client.delete(f'/api/student/{sid}')
    assert res.status_code == 200

    assert client.get(f'/api/student/{sid}').status_code == 404

def test_student_delete_not_found(client):
    res = client.delete('/api/student/999')
    assert res.status_code == 404


# =========================================================
# Enrollment API Tests
# =========================================================

def test_enrollment_get_invalid_student_id(client):
    res = client.get('/api/student/999/course')
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "ENROLLMENT002"
    assert data["error_message"] == "Student does not exist."

def test_enrollment_get_no_enrollments(client):
    p = client.post('/api/student', json={"first_name": "S1", "roll_number": "R1"})
    sid = p.get_json()["student_id"]

    res = client.get(f'/api/student/{sid}/course')
    assert res.status_code == 404

def test_enrollment_post_student_not_found(client):
    res = client.post('/api/student/999/course', json={"course_id": 1})
    assert res.status_code == 404

def test_enrollment_post_missing_course_id(client):
    p = client.post('/api/student', json={"first_name": "S1", "roll_number": "R1"})
    sid = p.get_json()["student_id"]

    res = client.post(f'/api/student/{sid}/course', json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "ENROLLMENT001"
    assert data["error_message"] == "Course does not exist"

def test_enrollment_post_nonexistent_course_id(client):
    p = client.post('/api/student', json={"first_name": "S1", "roll_number": "R1"})
    sid = p.get_json()["student_id"]

    res = client.post(f'/api/student/{sid}/course', json={"course_id": 999})
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "ENROLLMENT001"
    assert data["error_message"] == "Course does not exist"

def test_enrollment_post_success(client):
    p_student = client.post('/api/student', json={"first_name": "Narendra", "last_name": "Mishra", "roll_number": "MA19M010"})
    sid = p_student.get_json()["student_id"]

    p_course = client.post('/api/course', json={"course_name": "Maths1", "course_code": "MA101"})
    cid = p_course.get_json()["course_id"]

    res = client.post(f'/api/student/{sid}/course', json={"course_id": cid})
    assert res.status_code == 201
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["student_id"] == sid
    assert data[0]["course_id"] == cid
    assert "enrollment_id" in data[0]

def test_enrollment_get_success(client):
    p_student = client.post('/api/student', json={"first_name": "Narendra", "last_name": "Mishra", "roll_number": "MA19M010"})
    sid = p_student.get_json()["student_id"]

    p_course1 = client.post('/api/course', json={"course_name": "Maths1", "course_code": "MA101"})
    cid1 = p_course1.get_json()["course_id"]

    p_course2 = client.post('/api/course', json={"course_name": "Physics1", "course_code": "PH101"})
    cid2 = p_course2.get_json()["course_id"]

    client.post(f'/api/student/{sid}/course', json={"course_id": cid1})
    client.post(f'/api/student/{sid}/course', json={"course_id": cid2})

    res = client.get(f'/api/student/{sid}/course')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    c_ids = [item["course_id"] for item in data]
    assert cid1 in c_ids
    assert cid2 in c_ids

def test_enrollment_delete_invalid_student(client):
    p_course = client.post('/api/course', json={"course_name": "Maths1", "course_code": "MA101"})
    cid = p_course.get_json()["course_id"]

    res = client.delete(f'/api/student/999/course/{cid}')
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "ENROLLMENT002"
    assert data["error_message"] == "Student does not exist."

def test_enrollment_delete_invalid_course(client):
    p_student = client.post('/api/student', json={"first_name": "Narendra", "roll_number": "MA19M010"})
    sid = p_student.get_json()["student_id"]

    res = client.delete(f'/api/student/{sid}/course/999')
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_code"] == "ENROLLMENT001"
    assert data["error_message"] == "Course does not exist"

def test_enrollment_delete_not_enrolled(client):
    p_student = client.post('/api/student', json={"first_name": "Narendra", "roll_number": "MA19M010"})
    sid = p_student.get_json()["student_id"]

    p_course = client.post('/api/course', json={"course_name": "Maths1", "course_code": "MA101"})
    cid = p_course.get_json()["course_id"]

    res = client.delete(f'/api/student/{sid}/course/{cid}')
    assert res.status_code == 404

def test_enrollment_delete_success(client):
    p_student = client.post('/api/student', json={"first_name": "Narendra", "roll_number": "MA19M010"})
    sid = p_student.get_json()["student_id"]

    p_course = client.post('/api/course', json={"course_name": "Maths1", "course_code": "MA101"})
    cid = p_course.get_json()["course_id"]

    client.post(f'/api/student/{sid}/course', json={"course_id": cid})

    res = client.delete(f'/api/student/{sid}/course/{cid}')
    assert res.status_code == 200

    # Getting enrollments now should return 404 because student is no longer enrolled
    assert client.get(f'/api/student/{sid}/course').status_code == 404

def test_cascade_delete_course_removes_enrollment(client):
    p_student = client.post('/api/student', json={"first_name": "Narendra", "roll_number": "MA19M010"})
    sid = p_student.get_json()["student_id"]

    p_course = client.post('/api/course', json={"course_name": "Maths1", "course_code": "MA101"})
    cid = p_course.get_json()["course_id"]

    client.post(f'/api/student/{sid}/course', json={"course_id": cid})

    # Delete course
    client.delete(f'/api/course/{cid}')

    # Student shouldn't have any enrollments now
    res = client.get(f'/api/student/{sid}/course')
    assert res.status_code == 404

def test_cascade_delete_student_removes_enrollment(client):
    p_student = client.post('/api/student', json={"first_name": "Narendra", "roll_number": "MA19M010"})
    sid = p_student.get_json()["student_id"]

    p_course = client.post('/api/course', json={"course_name": "Maths1", "course_code": "MA101"})
    cid = p_course.get_json()["course_id"]

    client.post(f'/api/student/{sid}/course', json={"course_id": cid})

    # Delete student
    client.delete(f'/api/student/{sid}')

    # Student does not exist
    res = client.get(f'/api/student/{sid}/course')
    assert res.status_code == 400
    assert res.get_json()["error_code"] == "ENROLLMENT002"
