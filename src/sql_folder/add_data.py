import random
import string
from faker import Faker
from src.sql_folder.create_tables import db, Group, Course, Student

fake = Faker()


def generate_groups():
    for _ in range(10):
        group_name = ''.join([
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_uppercase),
            '-',
            str(random.randint(10, 99))
        ])
        group = Group(name=group_name)
        db.session.add(group)
    db.session.commit()


def generate_courses():
    course_names = ["Mathematics", "Biology", "Physics", "Chemistry", "History",
                    "English", "Informatics", "Art", "Music", "Geography"]
    for course_name in course_names:
        course = Course(name=course_name)
        db.session.add(course)
    db.session.commit()


def generate_students():
    first_names = [fake.first_name() for _ in range(20)]
    last_names = [fake.last_name() for _ in range(20)]

    for _ in range(200):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        student = Student(first_name=first_name, last_name=last_name)
        db.session.add(student)
    db.session.commit()


def assign_students_to_groups():
    groups = Group.query.all()
    students = Student.query.all()

    for student in students:
        group = random.choice(groups) if random.random() > 0.2 else None
        if group:
            group.students.append(student)
    db.session.commit()


def assign_courses_to_students():
    students = Student.query.all()
    courses = Course.query.all()

    for student in students:
        num_courses = random.randint(1, 3)
        selected_courses = random.sample(courses, num_courses)
        student.courses.extend(selected_courses)
    db.session.commit()

