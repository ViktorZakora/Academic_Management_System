from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vik:ubnfhf@localhost/task_10_sql'
db = SQLAlchemy(app)


student_course_association = db.Table(
    'student_course_association',
    db.Column('student_id', db.Integer, db.ForeignKey('Students.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('Courses.id'))
)


student_group_association = db.Table(
    'student_group_association',
    db.Column('student_id', db.Integer, db.ForeignKey('Students.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('Groups.id'))
)


class Group(db.Model):
    __tablename__ = 'Groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    students = relationship('Student', secondary=student_group_association, back_populates='groups')


class Student(db.Model):
    __tablename__ = 'Students'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    courses = relationship('Course', secondary=student_course_association, back_populates='students')
    groups = relationship('Group', secondary=student_group_association, back_populates='students')


class Course(db.Model):
    __tablename__ = 'Courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    students = relationship('Student', secondary=student_course_association, back_populates='courses')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # створити
        # db.drop_all()  # видалити
