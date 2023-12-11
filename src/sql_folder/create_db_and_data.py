from src.sql_folder.sql_file import create_app
from src.sql_folder.config import RealConfig
from src.sql_folder.create_tables import db
from src.sql_folder.add_data import generate_groups, generate_courses, generate_students, assign_students_to_groups, \
    assign_courses_to_students

app = create_app(RealConfig)


@app.cli.command('create_db')
def create_db_command():
    """
    Create the database with groups, courses, and students.
    """
    with app.app_context():
        db.create_all()  # створити усі таблиці
        print('Tables are created.')
        generate_groups()
        generate_courses()
        generate_students()
        assign_students_to_groups()
        assign_courses_to_students()
        print('Data is added.')


@app.cli.command('delete_db')
def delete_db_command():
    """
    Delete the database with groups, courses, and students.
    """
    with app.app_context():
        db.drop_all()  # видалити усі таблиці
        print('All tables are deleted.')