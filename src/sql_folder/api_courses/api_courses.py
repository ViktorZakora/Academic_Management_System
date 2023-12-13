from flask import Blueprint, request
from flask_restful import Api, Resource
from src.sql_folder.create_tables import db, Student, Course

api_courses = Blueprint('api_courses', __name__)

api = Api()
api.init_app(api_courses)


class Courses(Resource):
    def get(self):
        """
        Get all courses.

        This endpoint returns a list of all courses.

        ---
        tags:
          - Courses
        responses:
          200:
            description: List of all courses.
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
        """
        courses = Course.query.all()

        if courses:
            result = [{'id': course.id, 'name': course.name} for course in courses]
            return result, 200

    def post(self):
        """
        Add a new course.

        This endpoint allows you to add a new course.

        ---
        tags:
          - Courses
        parameters:
          - name: name
            in: query
            type: string
            required: true
            description: The name of the new course.
        responses:
          201:
            description: Course added successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The course has been successfully added.
          409:
            description: Course with the specified name already exists.
        """
        name = request.args.get('name')
        existing_course = Course.query.filter_by(name=name).first()

        if existing_course:
            return {'message': 'Course with the specified name already exists.'}, 409

        new_course = Course(name=name)
        db.session.add(new_course)
        db.session.commit()

        return {'message': 'The course has been successfully added.'}, 201


class CourseId(Resource):
    def get(self, course_id):
        """
        Get course by course_id.

        This endpoint returns a course based on their course_id.

        ---
        tags:
          - Courses
        parameters:
          - name: course_id
            in: path
            type: integer
            required: true
            description: The ID of the course.
        responses:
          200:
            description: Course information.
            schema:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
          404:
            description: Course not found.
        """
        course = Course.query.get(course_id)

        if course:
            result = {'id': course.id, 'name': course.name}
            return result, 200
        else:
            return {'message': 'Course not found.'}, 404

    def delete(self, course_id):
        """
        Delete a course by course_id.

        This endpoint allows you to delete a course based on their course_id.

        ---
        tags:
          - Courses
        parameters:
          - name: course_id
            in: path
            type: integer
            required: true
            description: The ID of the course to be deleted.
        responses:
          200:
            description: Course deleted successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The course has been successfully deleted.
          404:
            description: Course not found.
        """
        course = Course.query.get(course_id)

        if course:
            db.session.delete(course)
            db.session.commit()
            return {'message': 'The course has been successfully deleted.'}, 200
        else:
            return {'message': 'Course not found.'}, 404

    def put(self, course_id):
        """
        Update a course by course_id.

        This endpoint allows you to update a course's information based on their course_id.

        ---
        tags:
          - Courses
        parameters:
          - name: course_id
            in: path
            type: integer
            required: true
            description: The ID of the course to be updated.
          - name: name
            in: query
            type: string
            required: true
            description: The updated name of the course.
        responses:
          200:
            description: Course updated successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The course has been successfully updated.
          404:
            description: Course not found.
        """
        name = request.args.get('name')
        course = Course.query.get(course_id)

        if course:
            course.name = name
            db.session.commit()
            return {'message': 'The course has been successfully updated.'}, 200
        else:
            return {'message': 'Course not found.'}, 404


class CourseToStudents(Resource):
    def get(self, course_id):
        """
        Get students for a course.

        This endpoint returns a list of students associated with a course based on course_id.

        ---
        tags:
          - Courses
        parameters:
          - name: course_id
            in: path
            type: integer
            required: true
            description: The ID of the course.
        responses:
          200:
            description: List of students for the course.
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
            description: Course not found.
        """
        course = Course.query.get(course_id)

        if not course:
            return {'message': 'Course not found.'}, 404

        students = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name} for student in course.students]
        return students, 200

    def post(self, course_id):
        """
        Add a student to the course.

        This endpoint allows you to add a student to the course.

        ---
        tags:
          - Courses
        parameters:
          - name: course_id
            in: path
            type: integer
            required: true
            description: The ID of the course.
          - name: student_id
            in: query
            type: integer
            required: true
            description: The ID of the student to be added to the course.
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
            description: Student not found or Course not found.
          409:
            description: The student is already enrolled in the course.
        """
        course = Course.query.get(course_id)
        student_id = request.args.get('student_id')
        student = Student.query.filter_by(id=student_id).first()

        if not student:
            return {'message': 'Student not found.'}, 404

        if not course:
            return {'message': 'Course not found.'}, 404

        if student in course.students:
            return {'message': 'The student is already enrolled in the course.'}, 409

        course.students.append(student)
        db.session.commit()
        return {'message': 'The student has been successfully added to the course.'}, 200


class CourseDelStudents(Resource):
    def delete(self, course_id, student_id):
        """
        Remove a student from the course.

        This endpoint allows you to remove a student from the course.

        ---
        tags:
          - Courses
        parameters:
          - name: course_id
            in: path
            type: integer
            required: true
            description: The ID of the course.
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the student to be added to the course.
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
            description: Student not found or Course not found.
          409:
            description: The student is not enrolled in the course.
        """
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)

        if not student:
            return {'message': 'Student not found.'}, 404

        if not course:
            return {'message': 'Course not found.'}, 404

        if student not in course.students:
            return {'message': 'The student is not enrolled in the course.'}, 409

        course.students.remove(student)
        db.session.commit()
        return {'message': 'The student has been successfully removed from the course.'}, 200


api.add_resource(Courses, '/courses')
api.add_resource(CourseId, '/courses/<int:course_id>')
api.add_resource(CourseToStudents, '/courses/<int:course_id>/students')
api.add_resource(CourseDelStudents, '/courses/<int:course_id>/students/<int:student_id>')
