from ..models import User
from ..api_1_0 import api
from flask import jsonify, g
from .errors import unauthorized, forbidden
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

# 验证身份
@auth.verify_password
def verify_password(email_or_token, passwd):
    if email_or_token == '':
        return False
    if passwd == '':
        g.current_user = User.varify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.varify_password(passwd)

@auth.error_handler
def auth_error():
    return unauthorized('未认证！')

# 用before_request与login_required实现每个api都要先验证后访问
@api.before_request
@auth.login_required
def before_request():
    if not g.current_user:
        return forbidden('没有访问权限！')

@api.route('/token')
def get_token():
    if not g.token_used:
        return jsonify({'token': g.current_user.generate_token(expiration=3600).decode('utf-8'), 'expiration': 3600})
    return unauthorized('令牌已存在！')

