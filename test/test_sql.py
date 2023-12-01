import pytest
import re

from src.sql_folder.add_data import generate_groups, generate_courses
from src.sql_folder.create_tables import db, Group, Student, Course, TestConfig
from src.sql_folder.sql_file import create_app


@pytest.fixture
def client():
    app = create_app(TestConfig)

    with app.test_client() as client:
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
            course1.students.append(student1)
            course2.students.append(student2)
            course3.students.append(student2)
            group1.students.append(student1)
            group2.students.append(student2)
            db.session.add_all([student1, student2, course1, course2, course3, course4, group1, group2])
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()


def test_courses(client):
    response = client.get('/courses')
    assert response.status_code == 200
    assert response.json == {'courses': [[1, 'Math'], [2, 'Science'], [3, 'Physics'], [4, 'Flask']]}

    response = client.post('/courses', query_string={'name': 'Python'})
    assert response.status_code == 201
    assert response.json == {'message': 'The course has been successfully added.'}

    response = client.post('/courses', query_string={'name': 'Python'})
    assert response.status_code == 409
    assert response.json == {'message': 'Course with the specified name already exists.'}

    response = client.get('/courses/1')
    assert response.status_code == 200
    assert response.json == [1, 'Math']

    response = client.get('/courses/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.delete('/courses/5')
    assert response.status_code == 200
    assert response.json == {'message': 'The course has been successfully deleted.'}

    response = client.delete('/courses/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.put('/courses/2', query_string={'name': 'Java'})
    assert response.status_code == 200
    assert response.json == {'message': 'The course has been successfully updated.'}

    response = client.put('/courses/10', query_string={'name': 'Java'})
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.get('/courses/course-to-students', query_string={'name_course': 'Art'})
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found with the name: Art'}

    response = client.get('/courses/course-to-students', query_string={'name_course': 'Physics'})
    assert response.status_code == 200
    assert response.json == {'students': [{'2': ['Jane', 'Smith']}]}

    response = client.get('/courses/course-to-students', query_string={'name_course': 'Flask'})
    assert response.status_code == 409
    assert response.json == {'message': f'No students found for the given course name: Flask.'}


def test_groups(client):
    response = client.get('/groups')
    assert response.status_code == 200
    assert response.json == {'groups': [[1, 'CV-42'], [2, 'HB-17']]}

    response = client.post('/groups', query_string={'name': 'QW-27'})
    assert response.status_code == 201
    assert response.json == {'message': 'The group has been successfully added.'}

    response = client.post('/groups', query_string={'name': 'QW-27'})
    assert response.status_code == 409
    assert response.json == {'message': 'Group with the specified name already exists.'}

    response = client.get('/groups/1')
    assert response.status_code == 200
    assert response.json == [1, 'CV-42']

    response = client.get('/groups/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.delete('/groups/3')
    assert response.status_code == 200
    assert response.json == {'message': 'The group has been successfully deleted.'}

    response = client.delete('/groups/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.put('/groups/1', query_string={'name': 'DB-27'})
    assert response.status_code == 200
    assert response.json == {'message': 'The group has been successfully updated.'}

    response = client.put('/groups/10', query_string={'name': 'DB-27'})
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.get('/groups/less-or-equal', query_string={'number': '2'})
    assert response.status_code == 200
    assert response.json == {'groups': [{'id': 1, 'name': 'DB-27'}, {'id': 2, 'name': 'HB-17'}]}


def test_students(client):
    response = client.get('/students')
    assert response.status_code == 200
    assert response.json == {'students': [[1, 'John', 'Doe'], [2, 'Jane', 'Smith']]}

    response = client.post('/students', query_string={'first_name': 'Alice', 'last_name': 'Johnson'})
    assert response.status_code == 201
    assert response.json == {'message': 'The student has been successfully added.'}

    response = client.post('/students', query_string={'first_name': 'Alice', 'last_name': 'Johnson'})
    assert response.status_code == 409
    assert response.json == {'message': 'Student with the specified first_name and last_name already exists.'}

    response = client.get('/students/1')
    assert response.status_code == 200
    assert response.json == [1, 'John', 'Doe']

    response = client.get('/students/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.delete('/students/3')
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully deleted.'}

    response = client.delete('/students/10')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.put('/students/2', query_string={'first_name': 'Bob', 'last_name': 'Marley'})
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully updated.'}

    response = client.put('/students/10', query_string={'first_name': 'Bob', 'last_name': 'Marley'})
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.get('/students/10/student-to-course')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.get('/students/1/student-to-course')
    assert response.status_code == 200
    assert response.json == {'courses': [{'id': 1, 'name': 'Math', 'description': None}]}

    response = client.post('/students/10/student-to-course', query_string={'name_course': 'Science'})
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.post('/students/2/student-to-course', query_string={'name_course': 'Math'})
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully added to the course.'}

    response = client.post('/students/2/student-to-course', query_string={'name_course': 'Science'})
    assert response.status_code == 409
    assert response.json == {'message': 'The student is already enrolled in the course.'}

    response = client.delete('/students/10/student-to-course', query_string={'name_course': 'Science'})
    assert response.status_code == 404
    assert response.json == {'message': 'Student or course not found.'}

    response = client.delete('/students/2/student-to-course', query_string={'name_course': 'Math'})
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully removed from the course.'}

    response = client.delete('/students/2/student-to-course', query_string={'name_course': 'Math'})
    assert response.status_code == 409
    assert response.json == {'message': 'The student is not enrolled in the course.'}


if __name__ == '__main__':
    pytest.main()