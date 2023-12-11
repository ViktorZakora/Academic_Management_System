import pytest
from src.sql_folder.config import TestConfig
from src.sql_folder.create_tables import db, Group, Student, Course
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
            group3 = Group(name='NB_98')
            course1.students.append(student1)
            course2.students.append(student2)
            course3.students.append(student2)
            group1.students.append(student1)
            group2.students.append(student2)
            db.session.add_all([student1, student2, course1, course2, course3, course4, group1, group2, group3])
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()


def test_courses(client):
    response = client.get('/courses')
    assert response.status_code == 200
    assert response.json == {'courses': [{'1': 'Math'}, {'2': 'Science'}, {'3': 'Physics'}, {'4': 'Flask'}]}

    response = client.post('/courses', query_string={'name': 'Python'})
    assert response.status_code == 201
    assert response.json == {'message': 'The course has been successfully added.'}

    response = client.post('/courses', query_string={'name': 'Python'})
    assert response.status_code == 409
    assert response.json == {'message': 'Course with the specified name already exists.'}

    response = client.get('/courses/1')
    assert response.status_code == 200
    assert response.json == {'1': 'Math'}

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

    response = client.get('/courses/10/students')
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.get('/courses/1/students')
    assert response.status_code == 200
    assert response.json == {'students': [{'1': ['John', 'Doe']}]}

    response = client.post('/courses/10/students', query_string={'student_id': '1'})
    assert response.status_code == 404
    assert response.json == {'message': 'Course not found.'}

    response = client.post('/courses/1/students', query_string={'student_id': '10'})
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.post('/courses/1/students', query_string={'student_id': '1'})
    assert response.status_code == 409
    assert response.json == {'message': 'The student is already enrolled in the course.'}

    response = client.post('/courses/1/students', query_string={'student_id': '2'})
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully added to the course.'}

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
    response = client.get('/groups')
    assert response.status_code == 200
    assert response.json == {'groups': [{'1': 'CV-42'}, {'2': 'HB-17'}, {'3': 'NB_98'}]}

    response = client.post('/groups', query_string={'name': 'QW-27'})
    assert response.status_code == 201
    assert response.json == {'message': 'The group has been successfully added.'}

    response = client.post('/groups', query_string={'name': 'QW-27'})
    assert response.status_code == 409
    assert response.json == {'message': 'Group with the specified name already exists.'}

    response = client.get('/groups', query_string={'count': '2'})
    assert response.status_code == 200
    assert response.json == {'groups': [{'1': 'CV-42'}, {'2': 'HB-17'}, {'3': 'NB_98'}, {'4': 'QW-27'}]}

    response = client.get('/groups/1')
    assert response.status_code == 200
    assert response.json == {'1': 'CV-42'}

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

    response = client.get('/groups/10/students')
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.get('/groups/1/students')
    assert response.status_code == 200
    assert response.json == {'students': [{'1': ['John', 'Doe']}]}

    response = client.post('/groups/10/students', query_string={'student_id': '1'})
    assert response.status_code == 404
    assert response.json == {'message': 'Group not found.'}

    response = client.post('/groups/1/students', query_string={'student_id': '10'})
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.post('/groups/1/students', query_string={'student_id': '1'})
    assert response.status_code == 409
    assert response.json == {'message': 'The student is already enrolled in the group.'}

    response = client.post('/groups/1/students', query_string={'student_id': '2'})
    assert response.status_code == 409
    assert response.json == {'message': 'The student is already enrolled in another group.'}

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

    response = client.post('/groups/1/students', query_string={'student_id': '1'})
    assert response.status_code == 200
    assert response.json == {'message': 'The student has been successfully added to the group.'}


def test_students(client):
    response = client.get('/students')
    assert response.status_code == 200
    assert response.json == {'students': [{'1': ['John', 'Doe']}, {'2': ['Jane', 'Smith']}]}

    response = client.post('/students', query_string={'first_name': 'Alice', 'last_name': 'Johnson'})
    assert response.status_code == 201
    assert response.json == {'message': 'The student has been successfully added.'}

    response = client.post('/students', query_string={'first_name': 'Alice', 'last_name': 'Johnson'})
    assert response.status_code == 409
    assert response.json == {'message': 'Student with the specified first_name and last_name already exists.'}

    response = client.get('/students/1')
    assert response.status_code == 200
    assert response.json == {'1': ['John', 'Doe']}

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

    response = client.get('/students/10/courses')
    assert response.status_code == 404
    assert response.json == {'message': 'Student not found.'}

    response = client.get('/students/1/courses')
    assert response.status_code == 200
    assert response.json == {'courses': [{'1': ['Math', None]}]}


if __name__ == '__main__':
    pytest.main()