import unittest
from flask import current_app
from app import creat_app, db

class BaseicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = creat_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @unittest.skip('跳过测试生成app')
    def test_app_exists(self):
        """测试是否成功生成app"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """测试是否处于测试环境"""
        self.assertTrue(current_app.config['TESTING'])
