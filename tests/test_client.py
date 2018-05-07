import re
import unittest
from app import creat_app, db
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = creat_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('url_for(\'main.index\')')
        self.assertTrue('登录' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post(url_for('auth.register'),data={
            'email': 'qiuyue@cug.edu.cn',
            'username': '我爱吃苦瓜',
            'password': 'A19990701',
            'password2': 'A19990701',
        })
        self.assertTrue(response.status_code == 302)

        # 使用新账号登录登录
        response = self.client.post(url_for('auth.login'),data={
            'email': 'qiuyue@cug.edu.cn',
            'password': 'A19990701',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search(r'我的信息', data))

        # 退出
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('您已成功退出登录' in data)