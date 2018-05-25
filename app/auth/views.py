from flask import render_template,redirect,request,url_for,flash,session,abort
from . import auth
from .forms import LoginForm,RegistrationForm,ResetPwForm,SetPwForm
from flask_login import login_user,logout_user,login_required,current_user
from ..models import User
from app import db
from smtplib import SMTP
from datetime import datetime
from hashlib import md5
from email.mime.text import MIMEText
from email.header import Header

@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.varify_password(form.password.data):
            # login_user()将用户设为登录状态
            login_user(user, form.remember.data)
            return redirect(url_for('main.index'))
        flash('用户名或密码错误！')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    # logout_user()将用户设置为登出状态
    logout_user()
    flash('您已成功退出登录')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/changepw',methods=['GET','POST'])
def changepw():
    form = ResetPwForm()
    if form.validate_on_submit():
        token = md5(str(datetime.utcnow()).encode('utf-8')).hexdigest()
        url = 'http://127.0.0.1:5000/auth/setpw/' + str(token)
        session['token'] = token
        session['email'] = form.email.data
        msg = MIMEText('请点击这个这个链接完成验证%s' % url, 'plain', 'utf-8')
        msg['From'] = 'qiuyueqy@qq.com'
        msg['To'] = form.email.data
        msg['Subject'] = Header('验证邮件', 'utf-8')
        smtp = SMTP()
        smtp.connect(host='smtp.qq.com', port=587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('qiuyueqy@qq.com', 'qogafagaslcfjige')
        smtp.sendmail('qiuyueqy@qq.com', form.email.data,msg.as_string())
        flash('确认邮件已发送，请在确认邮件中完成验证')
        return redirect(url_for('auth.setpw', token=token))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/setpw/<token>',methods=['GET','POST'])
def setpw(token):
    form = SetPwForm()
    try:
        if token == session['token']:
            if form.validate_on_submit():
                user = User.query.filter_by(email=session['email']).first()
                user.reset_password(form.password.data)
                flash('密码修改成功！')
                del session['token']
                del session['email']
                return redirect( url_for('main.index') )
            return render_template('auth/reset_password.html', form=form)
        else:
            abort(404)
    except:
        abort(404)

@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        current_user.ping()

