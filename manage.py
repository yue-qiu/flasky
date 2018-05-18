import os
from tests.test_client import FlaskClientTestCase
from app import creat_app, db
from app.models import User
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = creat_app('Deflaut')
manager = Manager(app)
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app,db=db,User=User)

@manager.command
def test():
    """Run the unit test"""
    import unittest
    suit = unittest.TestSuite()
    suit.addTests(unittest.TestLoader().discover('tests'))
    with open(os.path.join(os.path.abspath('.'), 'test.txt'), 'w') as f:
        unittest.TextTestRunner(verbosity=2, stream=f).run(suit)

manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.run()