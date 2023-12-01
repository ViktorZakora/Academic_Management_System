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
          404:
            description: No groups found.
        """
        groups = Group.query.all()

        if groups:
            result = [[group.id, group.name] for group in groups]
            return {'groups': result}, 200
        else:
            return {'message': 'No groups found.'}, 404

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
            result = [group.id, group.name]
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


class GroupLessOrEqualStudents(Resource):
    def get(self):
        """
        Get groups with less or equal students count.

        This endpoint returns a list of groups with less or equal students count.

        ---
        tags:
          - Groups
        parameters:
          - name: number
            in: query
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
        """
        number = request.args.get('number')
        groups = Group.query.join(Group.students).group_by(Group.id).having(func.count(Student.id) <= number).all()

        if groups:
            return {'groups': [{'id': group.id, 'name': group.name} for group in groups]}, 200


api.add_resource(Groups, '/groups', )
api.add_resource(GroupId, '/groups/<int:group_id>')
api.add_resource(GroupLessOrEqualStudents, '/groups/less-or-equal')
