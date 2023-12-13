import pytest
from src.sql_folder.config import TestConfig
from src.sql_folder.create_tables import db, Group, Student, Course
from src.sql_folder.sql_file import create_app


@pytest.fixture
def flask_app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Додайте тестові дані до фіктивної бази даних
        student1 = Student(first_name='John', last_name='Doe')
        student2 = Student(first_name='Jane', last_name='Smith')
        course1 = Course(name='Math')
        course2 = Course(name='Science')
        course3 = Course(name='Physics')
        course4 = Course(name='Flask')
        group1 = Group(name='CV-42')
        group2 = Group(name='HB-17')
        group3 = Group(name='NB_98')
        group4 = Group(name='FU_42')
        course1.students.append(student1)
        course2.students.append(student2)
        course3.students.append(student2)
        group1.students.append(student1)
        db.session.add_all([student1, student2, course1, course2, course3,
                            course4, group1, group2, group3, group4])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        yield client


def test_courses(client):
    name_course = {'name': 'Python'}

    response = client.get('/courses')
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'name': 'Math'}, {'id': 2, 'name': 'Science'},
                             {'id': 3, 'name': 'Physics'}, {'id': 4, 'name': 'Flask'}]

    response = client.post('/courses', query_string=name_course)
    assert response.status_code == 201
    assert response.json == {'message': 'The course has been successfully added.'}

    response = client.post('/courses', query_string=name_course)
    assert response.status_code == 409
    assert response.json == {'message': 'Course with the specified name already exists.'}


def test_course_id(client):
    name_course = {'name': 'Java'}

    response = client.get('/courses/1')
    assert response.status_code == 200
    assert response.json == {'id': 1, 'name': 'Math'}

    response = client.get('/courses/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.delete('/courses/4')
    assert response.status_code == 200
    assert response.json == {'message': 'The course has been successfully deleted.'}

    response = client.delete('/courses/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.put('/courses/2', query_string=name_course)
    assert response.status_code == 200
    assert response.json == {'message': 'The course has been successfully updated.'}

    response = client.put('/courses/10', query_string=name_course)
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}


def test_course_to_students(client):
    student_1 = {'student_id': '1'}
    student_2 = {'student_id': '2'}
    student_3 = {'student_id': '3'}

    response = client.get('/courses/10/students')
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.get('/courses/1/students')
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'first_name': 'John', 'last_name': 'Doe'}]

    response = client.post('/courses/10/students', query_string=student_1)
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.post('/courses/1/students', query_string=student_3)
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.post('/courses/1/students', query_string=student_1)
    assert response.status_code == 409
    assert response.json == {'message': 'The student is already enrolled in the course.'}

    response = client.post('/courses/1/students', query_string=student_2)
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully added to the course.'}


def test_course_to_del_students(client):
    response = client.delete('/courses/10/students/1')
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.delete('/courses/1/students/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.delete('/courses/2/students/1')
    assert response.status_code == 409
    assert response.json == {'message': 'The student is not enrolled in the course.'}

    response = client.delete('/courses/1/students/1')
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully removed from the course.'}


def test_groups(client):
    name_group = {'name': 'QW-27'}
    count = {'count': '2'}

    response = client.get('/groups')
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'name': 'CV-42'}, {'id': 2, 'name': 'HB-17'},
                             {'id': 3, 'name': 'NB_98'}, {'id': 4, 'name': 'FU_42'}]

    response = client.post('/groups', query_string=name_group)
    assert response.status_code == 201
    assert response.json == {'message': 'The group has been successfully added.'}

    response = client.post('/groups', query_string=name_group)
    assert response.status_code == 409
    assert response.json == {'message': 'Group with the specified name already exists.'}

    response = client.get('/groups', query_string=count)
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'name': 'CV-42'}]


def test_group_id(client):
    name_group = {'name': 'DB-27'}
    response = client.get('/groups/1')
    assert response.status_code == 200
    assert response.json == {'id': 1, 'name': 'CV-42'}

    response = client.get('/groups/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.delete('/groups/3')
    assert response.status_code == 200
    assert response.json == {'message': 'The group has been successfully deleted.'}

    response = client.delete('/groups/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.put('/groups/1', query_string=name_group)
    assert response.status_code == 200
    assert response.json == {'message': 'The group has been successfully updated.'}

    response = client.put('/groups/10', query_string=name_group)
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}


def test_group_to_students(client):
    student_1 = {'student_id': '1'}
    student_2 = {'student_id': '2'}
    student_3 = {'student_id': '3'}

    response = client.get('/groups/10/students')
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.get('/groups/1/students')
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'first_name': 'John', 'last_name': 'Doe'}]

    response = client.post('/groups/10/students', query_string=student_1)
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.post('/groups/1/students', query_string=student_3)
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.post('/groups/1/students', query_string=student_1)
    assert response.status_code == 409
    assert response.json == {'message': 'The student is already enrolled in the group.'}

    response = client.post('/groups/2/students', query_string=student_1)
    assert response.status_code == 409
    assert response.json == {'message': 'The student is already enrolled in another group.'}

    response = client.post('/groups/1/students', query_string=student_2)
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully added to the group.'}


def test_group_del_students(client):
    response = client.delete('/groups/10/students/1')
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.delete('/groups/1/students/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.delete('/groups/2/students/1')
    assert response.status_code == 409
    assert response.json == {'message': 'The student is not enrolled in the group.'}

    response = client.delete('/groups/1/students/1')
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully removed from the group.'}


def test_students(client):
    student = {'first_name': 'Alice', 'last_name': 'Johnson'}

    response = client.get('/students')
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'first_name': 'John', 'last_name': 'Doe'},
                             {'id': 2, 'first_name': 'Jane', 'last_name': 'Smith'}]

    response = client.post('/students', query_string=student)
    assert response.status_code == 201
    assert response.json == {'message': 'The student has been successfully added.'}

    response = client.post('/students', query_string=student)
    assert response.status_code == 409
    assert response.json == {'message': 'Student with the specified first_name and last_name already exists.'}


def test_student_id(client):
    student = {'first_name': 'Bob', 'last_name': 'Marley'}

    response = client.get('/students/1')
    assert response.status_code == 200
    assert response.json == {'id': 1, 'first_name': 'John', 'last_name': 'Doe'}

    response = client.get('/students/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.delete('/students/2')
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully deleted.'}

    response = client.delete('/students/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.put('/students/1', query_string=student)
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully updated.'}

    response = client.put('/students/10', query_string=student)
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}


def test_student_to_course(client):
    response = client.get('/students/10/courses')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.get('/students/1/courses')
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'name': 'Math', 'description': None}]


if __name__ == '__main__':
    pytest.main()