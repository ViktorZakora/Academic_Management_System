from flask import Blueprint, request
from flask_restful import Api, Resource
from sqlalchemy import func
from src.sql_folder.create_tables import db, Group, Student

api_groups = Blueprint('api_groups', __name__)

api = Api()
api.init_app(api_groups)


class Groups(Resource):
    def get(self):
        """
        Get all groups.

        This endpoint returns a list of all groups.

        ---
        tags:
          - Groups
        parameters:
          - name: count
            in: query
            type: integer
            required: false
            description: The maximum number of students in a group.
        responses:
          200:
            description: List of all groups.
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
        """
        count = request.args.get('count', type=int)
        query = db.session.query(Group.id, Group.name)
        groups = Group.query.all()

        if groups:
            if count:
                query = query.join(Group.students).group_by(Group.id).having(func.count(Student.id) <= count)
                result = [{'id': group.id, 'name': group.name} for group in query]
            else:
                result = [{'id': group.id, 'name': group.name} for group in groups]

            return result, 200

    def post(self):
        """
        Add a new group.

        This endpoint allows you to add a new group.

        ---
        tags:
          - Groups
        parameters:
          - name: name
            in: query
            type: string
            required: true
            description: The name of the new group.
        responses:
          201:
            description: Group added successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The group has been successfully added.
          409:
            description: Group with the specified name already exists.
        """
        name = request.args.get('name')
        existing_group = Group.query.filter_by(name=name).first()

        if existing_group:
            return {'message': 'Group with the specified name already exists.'}, 409

        new_group = Group(name=name)
        db.session.add(new_group)
        db.session.commit()

        return {'message': 'The group has been successfully added.'}, 201


class GroupId(Resource):
    def get(self, group_id):
        """
        Get group by group_id.

        This endpoint returns a group based on their group_id.

        ---
        tags:
          - Groups
        parameters:
          - name: group_id
            in: path
            type: integer
            required: true
            description: The ID of the group.
        responses:
          200:
            description: Group information.
            schema:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
          404:
            description: Group not found.
        """
        group = Group.query.get(group_id)

        if group:
            result = {'id': group.id, 'name': group.name}
            return result, 200
        else:
            return {'message': 'Group not found.'}, 404

    def delete(self, group_id):
        """
        Delete a group by group_id.

        This endpoint allows you to delete a group based on their group_id.

        ---
        tags:
          - Groups
        parameters:
          - name: group_id
            in: path
            type: integer
            required: true
            description: The ID of the group to be deleted.
        responses:
          200:
            description: Group deleted successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The group has been successfully deleted.
          404:
            description: Group not found.
        """
        group = Group.query.get(group_id)

        if group:
            db.session.delete(group)
            db.session.commit()
            return {'message': 'The group has been successfully deleted.'}, 200
        else:
            return {'message': 'Group not found.'}, 404

    def put(self, group_id):
        """
        Update a group by group_id.

        This endpoint allows you to update a group's information based on their group_id.

        ---
        tags:
          - Groups
        parameters:
          - name: group_id
            in: path
            type: integer
            required: true
            description: The ID of the group to be updated.
          - name: name
            in: query
            type: string
            required: true
            description: The updated name of the group.
        responses:
          200:
            description: Group updated successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The group has been successfully updated.
          404:
            description: Group not found.
        """
        name = request.args.get('name')
        group = Group.query.get(group_id)

        if group:
            group.name = name
            db.session.commit()
            return {'message': 'The group has been successfully updated.'}, 200
        else:
            return {'message': 'Group not found.'}, 404


class GroupToStudents(Resource):
    def get(self, group_id):
        """
        Get students for a group.

        This endpoint returns a list of students associated with a group based on group_id.

        ---
        tags:
          - Groups
        parameters:
          - name: group_id
            in: path
            type: integer
            required: true
            description: The ID of the group.
        responses:
          200:
            description: List of students for the group.
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
            description: Group not found.
        """
        group = Group.query.get(group_id)

        if not group:
            return {'message': 'Group not found.'}, 404

        students = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name} for student in group.students]
        return students, 200

    def post(self, group_id):
        """
        Add a student to the group.

        This endpoint allows you to add a student to the group.

        ---
        tags:
          - Groups
        parameters:
          - name: group_id
            in: path
            type: integer
            required: true
            description: The ID of the group.
          - name: student_id
            in: query
            type: integer
            required: true
            description: The ID of the student to be added to the group.
        responses:
          200:
            description: Student added to the group successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully added to the group.
          404:
            description: Student not found or Group not found.
          409:
            description: The student is already enrolled in the group.
        """
        group = Group.query.get(group_id)
        student_id = request.args.get('student_id')
        student = Student.query.filter_by(id=student_id).first()

        if not student:
            return {'message': 'Student not found.'}, 404

        if not group:
            return {'message': 'Group not found.'}, 404

        if student in group.students:
            return {'message': 'The student is already enrolled in the group.'}, 409

        other_groups = Group.query.filter(Group.students.any(id=student_id), Group.id != group_id).all()
        if other_groups:
            return {'message': 'The student is already enrolled in another group.'}, 409

        group.students.append(student)
        db.session.commit()
        return {'message': 'The student has been successfully added to the group.'}, 200


class GroupDelStudents(Resource):
    def delete(self, group_id, student_id):
        """
        Remove a student from the group.

        This endpoint allows you to remove a student from the group.

        ---
        tags:
          - Groups
        parameters:
          - name: group_id
            in: path
            type: integer
            required: true
            description: The ID of the group.
          - name: student_id
            in: path
            type: integer
            required: true
            description: The ID of the student to be added to the group.
        responses:
          200:
            description: Student removed from the group successfully.
            schema:
              type: object
              properties:
                message:
                  type: string
                  default: The student has been successfully removed from the group.
          404:
            description: Student not found or Group not found.
          409:
            description: The student is not enrolled in the group.
        """
        student = Student.query.get(student_id)
        group = Group.query.get(group_id)

        if not student:
            return {'message': 'Student not found.'}, 404

        if not group:
            return {'message': 'Group not found.'}, 404

        if student not in group.students:
            return {'message': 'The student is not enrolled in the group.'}, 409

        group.students.remove(student)
        db.session.commit()
        return {'message': 'The student has been successfully removed from the group.'}, 200


api.add_resource(Groups, '/groups', )
api.add_resource(GroupId, '/groups/<int:group_id>')
api.add_resource(GroupToStudents, '/groups/<int:group_id>/students')
api.add_resource(GroupDelStudents, '/groups/<int:group_id>/students/<int:student_id>')
