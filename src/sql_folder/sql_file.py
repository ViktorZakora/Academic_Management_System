from flask import Flask
from flasgger import Swagger
from sqlalchemy import func
from src.sql_folder.api.api import api_bp
from src.sql_folder.create_tables import db
from src.sql_folder.add_data import (generate_groups, generate_courses,
                                     generate_students, assign_courses_to_students, assign_students_to_groups)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vik:ubnfhf@localhost/task_10_sql'
    db.init_app(app)

    app.register_blueprint(api_bp)

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



