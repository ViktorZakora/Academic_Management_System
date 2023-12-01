from flask import Flask
from flasgger import Swagger
from src.sql_folder.api_courses.api_courses import api_courses
from src.sql_folder.api_groups.api_groups import api_groups
from src.sql_folder.api_students.api_students import api_students
from src.sql_folder.create_tables import db
from src.sql_folder.add_data import (generate_groups, generate_courses,
                                     generate_students, assign_courses_to_students, assign_students_to_groups)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vik:ubnfhf@localhost/task_10_sql'
    db.init_app(app)

    app.register_blueprint(api_courses)
    app.register_blueprint(api_groups)
    app.register_blueprint(api_students)

    swagger = Swagger(app)


    # # Додавання даних:
    # with app.app_context():
    #     generate_groups()
    #     generate_courses()
    #     generate_students()
    #     assign_students_to_groups()
    #     assign_courses_to_students()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, host='127.0.0.1')



