import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = 'qiuyue'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    UPLOADED_PHOTOS_DEST = os.getcwd()

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:A19990701@localhost:3306/flask'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'data.sqlite')

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:A19990701@localhost:3306/flask_test'
    SERVER_NAME = '127.0.0.1:5000'


config = {
    'Development' : DevelopmentConfig,
    'Production' : ProductionConfig,
    'testing' : TestConfig,
    'Deflaut' : DevelopmentConfig,
}
