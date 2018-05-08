import re
import unittest
from app.models import Post
from flask import url_for
from app import creat_app, db

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
        """测试访问首页"""
        response = self.client.get('url_for(\'main.index\')')
        self.assertTrue('登录' in response.get_data(as_text=True))

    def test_register_and_login(self):
        """测试注册和登录"""
        response = self.client.post(url_for('auth.register'), data={
            'email': 'qiuyue@cug.edu.cn',
            'username': '我爱吃苦瓜',
            'password': 'A19990701',
            'password2': 'A19990701',
        })
        self.assertTrue(response.status_code == 302)

        # 使用新账号登录登录
        response = self.client.post(url_for('auth.login'), data={
            'email': 'qiuyue@cug.edu.cn',
            'password': 'A19990701',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search(r'我的信息', data))

    def test_post(self):
        """测试发表博客"""
        self.test_register_and_login()
        response = self.client.post(url_for('main.index'),data={
            'body': '测试发表博客',
            'submit': '提交',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertRegex(data,r'测试发表博客')

    def test_logout(self):
        """测试退出登录"""
        self.test_register_and_login()
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('您已成功退出登录' in data)

    def test_todo(self):
        """测试todoList"""
        self.test_register_and_login()
        response = self.client.post(url_for('main.to_do_list', username='我爱吃苦瓜'), data={
            'text': '测试todoList',
            'complete': 'False',
            'submit': '提交',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertRegex(data, r'测试todoList')

    def test_comment(self):
        """测试comment"""
        self.test_register_and_login()
        response = self.client.post(url_for('main.index'), data={
            'body': '测试发表博客',
            'submit': '提交',
        }, follow_redirects=True)
        post = Post.query.filter_by(body='测试发表博客').first()
        response = self.client.post(url_for('main.post', id=post.id), data={
            'body': '测试comment',
            'submit': '提交',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertRegex(data, r'测试comment')
