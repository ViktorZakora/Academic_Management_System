from flask import Blueprint, request
from flask_restful import Api, Resource
from src.sql_folder.create_tables import db, Student, Course, student_course_association

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
            return {'courses': result}, 200
        else:
            return {'message': 'No courses found.'}, 404

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
    def get(self):
        """
        Get students related to the course.

        This endpoint returns a list of students related to the course with a given name.

        ---
        tags:
          - Courses
        parameters:
          - name: name_course
            in: query
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
        name_course = request.args.get('name_course')
        course = Course.query.filter_by(name=name_course).first()

        if not course:
            return {'message': f'Course not found with the name: {name_course}'}, 404

        students = db.session.query(Student.id, Student.first_name, Student.last_name) \
            .join(student_course_association) \
            .join(Course) \
            .filter(Course.name == name_course) \
            .all()

        if students:
            result = [{student.id: [student.first_name, student.last_name]} for student in students]
            return {'students': result}, 200
        else:
            return {'message': f'No students found for the given course name: {name_course}.'}, 409


api.add_resource(Courses, '/courses')
api.add_resource(CourseId, '/courses/<int:course_id>')
api.add_resource(CourseToStudents, '/courses/course-to-students')
