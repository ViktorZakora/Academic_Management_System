from flask import Blueprint
from flask_restful import Api, Resource
from sqlalchemy import func
from src.sql_folder.create_tables import db, Group, Student, Course, student_course_association

api_bp = Blueprint('api', __name__)

api = Api()
api.init_app(api_bp)


class GroupLessOrEqualStudents(Resource):
    def get(self, number):
        """
        Get groups with less or equal students count.

        This endpoint returns a list of groups with less or equal students count.

        ---
        tags:
          - Groups
        parameters:
          - name: number
            in: path
            type: integer
            required: true
            description: The maximum number of students a group can have.
        responses:
          200:
            description: List of groups with less or equal students count.
            schema:
              type: object
              properties:
                groups:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
          404:
            description: No groups found.
        """
        groups = Group.query.join(Group.students).group_by(Group.id).having(func.count(Student.id) <= number).all()

        if groups:
            return {'groups': [{'id': group.id, 'name': group.name} for group in groups]}, 200
        else:
            return {'message': 'No groups found'}, 404


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


class AddStudent(Resource):
    def post(self, first_name, last_name):
        """
        Add a new student.

        This endpoint allows you to add a new student.

        ---
        tags:
          - Students
        parameters:
          - name: first_name
            in: path
            type: string
            required: true
            description: The first name of the student.
          - name: last_name
            in: path
            type: string
            required: true
            description: The last name of the student.
        responses:
          201:
            description: Student added successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully added.
        """
        new_student = Student(first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()

        return {'message': 'The student has been successfully added.'}, 201


class DeleteStudent(Resource):
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


class AddStudentToCourse(Resource):
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


class RemoveStudentFromCourse(Resource):
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


api.add_resource(GroupLessOrEqualStudents, '/group/<int:number>')
api.add_resource(StudentsByCourse, '/student/by_course/<string:name_course>')
api.add_resource(AddStudent, '/student/add_student/<string:first_name>/<string:last_name>')
api.add_resource(DeleteStudent, '/student/del_student/<int:student_id>')
api.add_resource(AddStudentToCourse, '/student/add_to_course/<int:student_id>/<string:name_course>')
api.add_resource(RemoveStudentFromCourse, '/student/del_to_course/<int:student_id>/<string:name_course>')

