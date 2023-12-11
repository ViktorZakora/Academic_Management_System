from flask import Flask
from flasgger import Swagger
from src.sql_folder.api_courses.api_courses import api_courses
from src.sql_folder.api_groups.api_groups import api_groups
from src.sql_folder.api_students.api_students import api_students
from src.sql_folder.create_tables import db
from src.sql_folder.config import RealConfig


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    app.register_blueprint(api_courses)
    app.register_blueprint(api_groups)
    app.register_blueprint(api_students)

    swagger = Swagger(app)

    return app


if __name__ == '__main__':
    app = create_app(RealConfig)
    app.run(debug=True, port=5000, host='127.0.0.1')
