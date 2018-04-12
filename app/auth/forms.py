from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,BooleanField,PasswordField
from wtforms.validators import DataRequired,Email,Length,EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email(),Length(1,64)])
    password = PasswordField('密码',validators=[DataRequired(),])
    remember = BooleanField('记住我')
    submit = SubmitField('提交')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('昵称',validators=[DataRequired(),Length(1,64)])
    password = PasswordField('密码',validators=[DataRequired(),EqualTo('password2',message='两次密码不一致，请再次输入')])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('提交')

    # 如果表单类中定义了以validate_开头，后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
    def validate_eamil(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email已经存在!')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该昵称已被占用')

class ResetPwForm(FlaskForm):
    email = StringField('你的Email',validators=(DataRequired(),Email()))
    submit = SubmitField('提交')

class SetPwForm(FlaskForm):
    password = PasswordField('新密码',validators=[DataRequired(),])
    password2 = PasswordField('确认密码',validators=[DataRequired(),EqualTo('password',message='两次密码不一致，请再次输入')])
    submit = SubmitField('提交')