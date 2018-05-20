from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from config import config
from flask import Flask,render_template
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_uploads import UploadSet,IMAGES,configure_uploads

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
login_manager = LoginManager()
pagedown = PageDown()
# 设置登录页面的端点
login_manager.login_view = 'auth.login'
photos = UploadSet('photos', IMAGES)

def creat_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    configure_uploads(app, photos)

    # 附加路由
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 前闭后开的url形式
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')

    return app
