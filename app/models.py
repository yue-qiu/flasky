from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from datetime import datetime
import hashlib
from flask import request
from markdown import markdown
import bleach


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # permissions的值是一个整数，表示位标识，各操作都表示一个位标识。
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean,default=False,index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """
        通过权限组合，创建有不同权限的角色
        匿名：只能浏览。所以不用在数据库设置这个角色。
        User:正常权限，可评论，发文章，关注别人。一般用户默认是User
        Moderator：协管员，可评论，发文章，关注别人，管理他人评论。
        Administrator：管理员，拥有最高权限。
        :return:
        """
        roles = {
             'User' : (Permission.FOLLOW|
                       Permission.COMMENT|
                       Permission.WRITE_ARTICLES,True),
             'Moderator' : (Permission.FOLLOW|
                            Permission.COMMENT|
                            Permission.WRITE_ARTICLES|
                            Permission.MODERATE_COMMENTS,False),
             'Administrator' : (0xff,False)
         }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
             role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
            db.session.commit()

    def __repr__(self):
     return '<Role %r>' % self.name

class Permission:
    '''
    对于flasky来说，不同操作代表着不同的权限，这个权限就由Role模型中的permissions字段代表
    操作的权限共使用8位来表示，每一位被设置为1都代表可以执行某项操作
    关注用户：0b00000001 (0x01)
    发表评论：0b00000010 (0x02)
    写文章： 0b00000100 (0x04)
    管理他人评论： 0b00001000 (0x08)
    管理员权限： 0b10000000 (0x80)
    比如一个可以关注别人，发表评论的用户，其权限代码为：0b00000011
    '''
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)


# flask-login要求模型实现至少四个方法：is_authenticated(),is_active(),is_anonymous(),get_id()
# 这四种方法也可以通过继承flask-login提供的UserMixin类来实现
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64),unique=True,index=True)
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    location = db.Column(db.String(128))
    member_since = db.Column(db.DateTime (),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash = db.Column(db.String(64))
    todo = db.relationship('To_Do',backref='author',lazy='dynamic')
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],backref=db.backref('follower',lazy='joined'),
                               lazy='dynamic',cascade='all,delete-orphan')
    follower = db.relationship('Follow',foreign_keys=[Follow.followed_id],backref=db.backref('followed',lazy='joined'),
                               lazy='dynamic',cascade='all,delete-orphan')
    comments = db.relationship('Comment',backref='author',lazy='dynamic')

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise ValueError('密码不可读！')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def varify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def reset_password(self,password):
        self.password_hash = generate_password_hash(password)

    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self,user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        if user.id is None:
            return False
        return self.follower.filter_by(follower_id=user.id).first() is not None

    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_Administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self,size=50,default='identicon',rating='g'):
        '''
        上传头像，要使用这个功能，先要在https://cn.gravatar.com/上注册自己的账号并上传图片
        图片上传成功后，其url值就是 http://www.gravatar.com/avatar + 邮箱MD5值 + 查询字段
        :param size:图片大小，以像素点为单位
        :param default:没有注册账号的用户使用的默认图片生成方式，可选值有 404（返回404错误），默认图片url，图片生成器： mm，
        identicon， wavatar，retro或blank等
        :param rating:图片级别，可选值有 g，pg，r和x
        :return: 用户头像url
        '''
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,hash=hash,size=size,default=default,rating=rating)

    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    comments = db.relationship('Comment',backref='post',lazy='dynamic')

    @staticmethod
    def on_changed_body(target,value,oldvalue,initator):
        allowed_tags = ['a','abbr','acronym','b','blockquote','code','em','i',
        'li','ol','pre','strong','ul','h1','h2','h3','p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_formal='html'),tags=allowed_tags,strip=True))

db.event.listen(Post.body,'set',Post.on_changed_body)

class To_Do(db.Model):
    __tablename__ = 'set_to_do_list'
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(512))
    text_html = db.Column(db.Text)
    complete = db.Column(db.Boolean())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_text(target,value,oldvalue,initator):
        allowed_tags = ['a','abbr','acronym','b','blockquote','code','em','i',
        'li','ol','pre','strong','ul','h1','h2','h3','p']
        target.text_html = bleach.linkify(bleach.clean(markdown(value,output_formal='html'),tags=allowed_tags,strip=True))

db.event.listen(To_Do.text,'set',To_Do.on_changed_text)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow,index=True)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','code','em','i','strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))

db.event.listen(Comment.body,'set',Comment.on_changed_body)

# flask-login要求实现一个回调函数，使用指定的标识符加载用户
@login_manager.user_loader
def load_user(user_id):
    """
    接受一个id值，在User中能查到这个id就返回这个对象，否则返回None
    :param user_id:
    :return:
    """
    return User.query.get(int(user_id))

