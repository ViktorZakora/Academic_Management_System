class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class RealConfig:
    SQLALCHEMY_DATABASE_URI = 'postgresql://vik:ubnfhf@localhost/task_10_sql'