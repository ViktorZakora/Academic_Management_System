from flask import Blueprint
from flask_restful import Api, Resource
from sqlalchemy import func
from src.sql_folder.create_tables import db, Group, Student, Course, student_course_association

api_students = Blueprint('api_students', __name__)

api = Api()
api.init_app(api_students)


class Students(Resource):
    def get(self):
        """
        Get all students.

        This endpoint returns a list of all students.

        ---
        tags:
          - Students
        responses:
          200:
            description: List of all students.
            schema:
              type: object
              properties:
                students:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      first_name:
                        type: string
                      last_name:
                        type: string
          404:
            description: No students found.
        """
        students = Student.query.all()

        if students:
            result = [[student.id, student.first_name, student.last_name] for student in students]
            return {'students': result}, 200
        else:
            return {'message': 'No students found.'}, 404


class StudentId(Resource):
    def get(self, student_id):
        """
        Get student by student_id.

        This endpoint returns a student based on their student_id.

        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the student.
        responses:
          200:
            description: Student information.
            schema:
              type: object
              properties:
                id:
                  type: integer
                first_name:
                  type: string
                last_name:
                  type: string
          404:
            description: Student not found.
        """
        student = Student.query.get(student_id)

        if student:
            result = [student.id, student.first_name, student.last_name]
            return result, 200
        else:
            return {'message': 'Student not found.'}, 404

    def delete(self, student_id):
        """
        Delete a student by student_id.

        This endpoint allows you to delete a student based on their student_id.

        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the student to be deleted.
        responses:
          200:
            description: Student deleted successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully deleted.
          404:
            description: Student not found.
        """
        student = Student.query.get(student_id)

        if student:
            db.session.delete(student)
            db.session.commit()
            return {'message': 'The student has been successfully deleted.'}, 200
        else:
            return {'message': 'Student not found.'}, 404


class StudentUpdate(Resource):
    def put(self, student_id, first_name, last_name):
        """
        Update a student by student_id.

        This endpoint allows you to update a student's information based on their student_id.

        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the student to be updated.
          - name: first_name
            in: path
            type: string
            required: true
            description: The updated first name of the student.
          - name: last_name
            in: path
            type: string
            required: true
            description: The updated last name of the student.
        responses:
          200:
            description: Student updated successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully updated.
          404:
            description: Student not found.
        """
        student = Student.query.get(student_id)

        if student:
            student.first_name = first_name
            student.last_name = last_name
            db.session.commit()
            return {'message': 'The student has been successfully updated.'}, 200
        else:
            return {'message': 'Student not found.'}, 404

    def post(self, student_id, first_name, last_name):
        """
        Add a new student.

        This endpoint allows you to add a new student.

        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the new student.
          - name: first_name
            in: path
            type: string
            required: true
            description: The first name of the new student.
          - name: last_name
            in: path
            type: string
            required: true
            description: The last name of the new student.
        responses:
          201:
            description: Student added successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully added.
          409:
            description: Student ID already exists.
        """
        existing_student = Student.query.get(student_id)

        if existing_student:
            return {'message': 'Student ID already exists.'}, 409

        new_student = Student(id=student_id, first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()

        return {'message': 'The student has been successfully added.'}, 201


class StudentToCourse(Resource):
    def post(self, student_id, name_course):
        """
        Add a student to the course.

        This endpoint allows you to add a student to the course.

        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the student to be added to the course.
          - name: name_course
            in: path
            type: string
            required: true
            description: The name of the course to which the student will be added.
        responses:
          200:
            description: Student added to the course successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully added to the course.
          404:
            description: Student or course not found.
          409:
            description: The student is already enrolled in the course.
        """
        student = Student.query.get(student_id)
        course = Course.query.filter_by(name=name_course).first()

        if student and course:
            if student in course.students:
                return {'message': 'The student is already enrolled in the course.'}, 409

            course.students.append(student)
            db.session.commit()
            return {'message': 'The student has been successfully added to the course.'}, 200
        else:
            return {'message': 'Student or course not found.'}, 404

    def delete(self, student_id, name_course):
        """
        Remove a student from the course.

        This endpoint allows you to remove a student from the course.

        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the student to be removed from the course.
          - name: name_course
            in: path
            type: string
            required: true
            description: The name of the course from which the student will be removed.
        responses:
          200:
            description: Student removed from the course successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully removed from the course.
          404:
            description: Student or course not found.
          409:
            description: The student is not enrolled in the course.
        """
        student = Student.query.get(student_id)
        course = Course.query.filter_by(name=name_course).first()

        if student and course:
            if student not in course.students:
                return {'message': 'The student is not enrolled in the course.'}, 409

            course.students.remove(student)
            db.session.commit()
            return {'message': 'The student has been successfully removed from the course.'}, 200
        else:
            return {'message': 'Student or course not found.'}, 404


class StudentsByCourse(Resource):
    def get(self, name_course):
        """
        Get students related to the course.

        This endpoint returns a list of students related to the course with a given name.

        ---
        tags:
          - Students
        parameters:
          - name: name_course
            in: path
            type: string
            required: true
            description: The name of the course.
        responses:
          200:
            description: List of students related to the course.
            schema:
              type: object
              properties:
                students:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      first_name:
                        type: string
                      last_name:
                        type: string
          404:
            description: No students found for the given course name.
        """
        students = Student.query.join(student_course_association).join(Course).filter(Course.name == name_course).all()

        if students:
            result = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name} for student in students]
            return {'students': result}, 200
        else:
            return {'message': f'No students found for the given course name ({name_course}).'}, 404


api.add_resource(Students, '/students',)
api.add_resource(StudentId, '/students/<int:student_id>')
api.add_resource(StudentUpdate, '/students/<int:student_id>/<string:first_name>/<string:last_name>')
api.add_resource(StudentToCourse, '/students/student-to-course/<int:student_id>/<string:name_course>')
api.add_resource(StudentsByCourse, '/students/student-by-course/<string:name_course>')
