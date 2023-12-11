from flask import Blueprint, request
from flask_restful import Api, Resource
from src.sql_folder.create_tables import db, Student, Course

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
                      name:
                        type: string
        """
        students = Student.query.all()

        if students:
            result = [{student.id: [student.first_name, student.last_name]} for student in students]
            return {'students': result}, 200

    def post(self):
        """
        Add a new student.

        This endpoint allows you to add a new student.

        ---
        tags:
          - Students
        parameters:
          - name: first_name
            in: query
            type: string
            required: true
            description: The first name of the new student.
          - name: last_name
            in: query
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
            description: Student with the specified name already exists.
        """
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        existing_student = Student.query.filter_by(first_name=first_name, last_name=last_name).first()

        if existing_student:
            return {'message': 'Student with the specified first_name and last_name already exists.'}, 409

        new_student = Student(first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()

        return {'message': 'The student has been successfully added.'}, 201


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
                name:
                  type: string
          404:
            description: Student not found.
        """
        student = Student.query.get(student_id)

        if student:
            result = {student.id: [student.first_name, student.last_name]}
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

    def put(self, student_id):
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
            description: The ID of the group to be updated.
          - name: first_name
            in: query
            type: string
            required: true
            description: The updated first_name of the student.
          - name: last_name
            in: query
            type: string
            required: true
            description: The updated last_name of the student.
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
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        student = Student.query.get(student_id)

        if student:
            student.first_name = first_name
            student.last_name = last_name
            db.session.commit()
            return {'message': 'The student has been successfully updated.'}, 200
        else:
            return {'message': 'Student not found.'}, 404


class StudentToCourse(Resource):
    def get(self, student_id):
        """
        Get courses for a student.

        This endpoint returns a list of courses associated with a student based on student_id.

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
            description: List of courses for the student.
            schema:
              type: object
              properties:
                courses:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
          404:
            description: Student not found.
        """
        student = Student.query.get(student_id)

        if not student:
            return {'message': 'Student not found.'}, 404

        courses = [{course.id: [course.name, course.description]} for course in student.courses]
        return {'courses': courses}, 200


api.add_resource(Students, '/students', )
api.add_resource(StudentId, '/students/<int:student_id>')
api.add_resource(StudentToCourse, '/students/<int:student_id>/courses')
