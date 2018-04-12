from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,BooleanField,PasswordField,TextAreaField,SelectField
from wtforms.validators import DataRequired,Length
from flask_pagedown.fields import PageDownField

class Nameform(FlaskForm):
    name = StringField('请输入用户名',validators=[DataRequired()])
    password = PasswordField('请输入密码',validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('提交')

class EditprofileForm(FlaskForm):
    name = StringField('姓名',validators=[Length(0,64)])
    location = StringField('住址',validators=[Length(0,64)])
    about_me = TextAreaField('关于我的信息')
    submit = SubmitField('提交')

class PostForm(FlaskForm):
    body = PageDownField('当我们在搬砖时我们都在说些什么:',validators=[DataRequired()])
    submit = SubmitField('提交')

class AddToDoForm(FlaskForm):
    text = TextAreaField('你有啥要做去做的事吗？',validators=[Length(0,512)])
    submit = SubmitField('提交')

class CommnetForm(FlaskForm):
    body = PageDownField('',validators=[DataRequired()])
    submit = SubmitField('提交')

class TravelForm(FlaskForm):
    way = SelectField('出行方式',choices=[
        ('bus','公交地铁（限市内）'),
        ('car','自助驾车（限省内）'),
    ])
    begin = StringField('起点',validators=[DataRequired()])
    end = StringField('终点',validators=[DataRequired()])
    submit = SubmitField('提交')
