import os
import click
from app import db, creat_app
from flask_migrate import Migrate

app = creat_app(os.getenv('FLASK_CONFIG') or 'Deflaut')
migrate = Migrate(app, db)

@app.cli.command()
def test():
    import unittest

    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().discover('tests'))
    unittest.TextTestRunner(verbosity=2).run(suite)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db)