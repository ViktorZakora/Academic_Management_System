from flask import Blueprint
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
          404:
            description: No courses found.
        """
        courses = Course.query.all()

        if courses:
            result = [[course.id, course.name] for course in courses]
            return {'coursess': result}, 200
        else:
            return {'message': 'No courses found.'}, 404


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
            result = [course.id, course.name]
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


class CourseUpdate(Resource):
    def put(self, course_id, name):
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
            in: path
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
        course = Course.query.get(course_id)

        if course:
            course.name = name
            db.session.commit()
            return {'message': 'The course has been successfully updated.'}, 200
        else:
            return {'message': 'Course not found.'}, 404

    def post(self, course_id, name):
        """
        Add a new course.

        This endpoint allows you to add a new course.

        ---
        tags:
          - Courses
        parameters:
          - name: course_id
            in: path
            type: integer
            required: true
            description: The ID of the new course.
          - name: name
            in: path
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
            description: Course ID already exists.
        """
        existing_course = Course.query.get(course_id)

        if existing_course:
            return {'message': 'Course ID already exists.'}, 409

        new_course = Course(id=course_id, name=name)
        db.session.add(new_course)
        db.session.commit()

        return {'message': 'The course has been successfully added.'}, 201


class CoursesByStudent(Resource):
    def get(self, student_id):
        """
        Get courses for a student.

        This endpoint returns a list of courses associated with a student based on student_id.

        ---
        tags:
          - Courses
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

        courses = [{'id': course.id, 'name': course.name, 'description': course.description} for course in student.courses]
        return {'courses': courses}, 200


api.add_resource(Courses, '/courses',)
api.add_resource(CourseId, '/courses/<int:course_id>')
api.add_resource(CourseUpdate, '/courses/<int:course_id>/<string:name>')
api.add_resource(CoursesByStudent, '/courses/courses-by-student/<int:student_id>')
