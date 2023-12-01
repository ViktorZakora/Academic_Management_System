# import pytest
# from src.sql_folder.sql_file import create_app
# from src.sql_folder.create_tables import TestConfig, Report, database_proxy
#
#
# @pytest.fixture
# def client():
#     app = create_app(TestConfig)
#     client = app.test_client()
#
#     database_proxy.create_tables([Report])
#
#     Report.create(
#         abbreviation='PGS',
#         driver='John Doe',
#         team='Team A',
#         time='2023-11-12 12:00:00'
#     )
#
#     yield client
#
#
# def test_index(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b"Monaco 2018 Racin" in response.data
#
#
# def test_report(client):
#     response = client.get('/report')
#     assert response.status_code == 200
#     assert b"Report" in response.data
#
#
# def test_all_drivers(client):
#     response = client.get('/report/all_drivers')
#     assert response.status_code == 200  # перевірка коду стану
#     assert b"All drivers" in response.data
#
#
# def test_process_data_2(client):
#     response = client.get('/report/all_drivers/process_data_2?key=John Doe')
#     assert response.status_code == 200
#     assert 'PGS' in response.get_data(as_text=True)  # чи ключ відображається на сторінці
#     assert 'John Doe' in response.get_data(as_text=True)  # чи значення відображається на сторінці
#
#
# def test_driver(client):
#     response = client.get('/driver')
#     assert response.status_code == 200
#
#
# def test_process_data(client):
#     response = client.post('/driver/process_data', data={'key': 'PGS'})
#     assert response.status_code == 200
#     assert 'PGS' in response.get_data(as_text=True)  # чи ключ відображається на сторінці
#     assert 'John Doe' in response.get_data(as_text=True)  # чи значення відображається на сторінці
#     assert 'Such a driver did not participate in the competition.' not in response.get_data(as_text=True)  # чи помилка не відображається
#
#
# def test_api_report_json(client):
#     response = client.get('http://localhost:5000/v1/report/?format=json')
#     assert response.status_code == 200
#     assert response.content_type == 'application/json'
#     assert response.json['PGS'] == ['John Doe', 'Team A', 'Sun, 12 Nov 2023 12:00:00 GMT']
#     assert response.json == {'PGS': ['John Doe', 'Team A', 'Sun, 12 Nov 2023 12:00:00 GMT']}
#     # Перевірка вмісту JSON відповіді
#
#
# def test_api_report_xml(client):
#     response = client.get('http://localhost:5000/v1/report/?format=xml')
#     assert response.status_code == 200
#     assert response.content_type == 'application/xml; charset=utf-8'
#     # Перевірка вмісту XML відповіді
#
#
# def test_api_report_error(client):
#     response = client.get('http://localhost:5000/v1/report/?format=html')
#     assert response.status_code == 200
#     assert response.content_type == 'application/json'
#     assert response.data == b'{"Error":"Unsupported format"}\n'
#     # Перевірка вмісту Error відповіді
#
#
# def test_api_all_drivers_json(client):
#     response = client.get('http://127.0.0.1:5000/v1/report/all_drivers/?format=json')
#     assert response.status_code == 200
#     assert response.content_type == 'application/json'
#     assert response.json['PGS'] == 'John Doe'
#     # Перевірка вмісту JSON відповіді
#
#
# def test_api_all_drivers_xml(client):
#     response = client.get('http://127.0.0.1:5000/v1/report/all_drivers/?format=xml')
#     assert response.status_code == 200
#     assert response.content_type == 'application/xml; charset=utf-8'
#     # Перевірка вмісту XML відповіді
#
#
# def test_api_all_drivers_error(client):
#     response = client.get('http://127.0.0.1:5000/v1/report/all_drivers/?format=html')
#     assert response.status_code == 200
#     assert response.content_type == 'application/json'
#     assert response.data == b'{"Error":"Unsupported format"}\n'
#     # Перевірка вмісту Error відповіді
#
# def test_insert_report(client):
#     reports = Report.select()
#     assert reports.count() == 1
#     report = reports[0]
#     assert report.abbreviation == 'PGS'
#     assert report.driver == 'John Doe'
#     assert report.team == 'Team A'
#     assert str(report.time) == '2023-11-12 12:00:00'
#
#
# if __name__ == '__main__':
#     pytest.main()

import pytest
from src.sql_folder.create_tables import app, db, Group, Student, Course


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = ":memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_students_by_course(client):
    # Add a course and some students
    course = Course(name='Math')
    db.session.add(course)
    db.session.commit()
    student1 = Student(first_name='John', last_name='Doe')
    student2 = Student(first_name='Jane', last_name='Doe')
    student3 = Student(first_name='Bob', last_name='Smith')
    db.session.add_all([student1, student2, student3])
    db.session.commit()
    course.students.append(student1)
    course.students.append(student2)
    db.session.commit()

    # Test with existing course
    response = client.get('/student/by_course/Math')
    assert response.status_code == 200
    assert response.json == {'students': [{'id': student1.id, 'first_name': 'John', 'last_name': 'Doe'}, {'id': student2.id, 'first_name': 'Jane', 'last_name': 'Doe'}]}

    # Test with non-existing course
    response = client.get('/student/by_course/History')
    assert response.status_code == 404
    assert response.json == {'message': 'No students found for the given course name (History).'}



if __name__ == '__main__':
    pytest.main()