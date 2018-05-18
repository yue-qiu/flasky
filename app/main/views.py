from flask import render_template,redirect,url_for,request,flash,abort,make_response,current_app
from datetime import datetime
from . import main
from .forms import Nameform,EditprofileForm,PostForm,AddToDoForm,CommnetForm,TravelForm
from .. import db
from ..models import User,Post,To_Do,Comment
from flask_login import login_required,current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, error_out=False, per_page=10
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,pagination=pagination,show_followed=show_followed)

@main.route('/user/<username>/')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, error_out=False, per_page=10
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,pagination=pagination)

@main.route('/checkpost/<int:id>/',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommnetForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        flash('评论成功!')
        return redirect(url_for('main.post',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    form.body.data = ''
    if page == -1:
        # 用于定位到表示最后一页
        page = (post.comments.count()) // 10 + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page,per_page=10,error_out=False
    )
    comments = pagination.items
    # 这里以一个列表的方式传递posts，因为_post.html中使用了for遍历
    return render_template('checkpost.html',posts=[post],form=form,comments=comments,pagination=pagination)

@main.route('/edit/<int:id>/')
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('修改成功！')
        return redirect(url_for('main.edit',id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

@main.route('/<username>/to_do_list/',methods=['GET','POST'])
@login_required
def to_do_list(username):
    form = AddToDoForm()
    if form.validate_on_submit():
        text = To_Do(text=form.text.data,complete=False,author=current_user._get_current_object())
        db.session.add(text)
        db.session.commit()
        return redirect(url_for('main.to_do_list',username=current_user.username))
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    pagination = user.todo.order_by(To_Do.timestamp.desc()).paginate(
        page, error_out=False,per_page=10
    )
    todos = pagination.items
    return render_template('to_do.html',form=form,todos=todos,pagination=pagination)

@main.route('/deleteToDo/<username>/<id>/',methods=['POST'])
@login_required
def deleteToDo(username,id):
    event = To_Do.query.get_or_404(int(id))
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('main.to_do_list',username=current_user.username))

@main.route('/deletePost/<username>/<id>/',methods=['POST'])
@login_required
def deletePost(username,id):
    post = Post.query.get_or_404(int(id))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('main.user',username=current_user.username))

@main.route('/follow/<username>/')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在！')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('你已经关注这个用户了~')
        return redirect(url_for('main.index'))
    current_user.follow(user)
    flash('关注成功！')
    return redirect(url_for('main.user',username=username))

@main.route('/unfollow/<username>/')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在！')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    flash('已经取消关注了~')
    return redirect(url_for('main.user',username=username))

@main.route('/<username>/follower/')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        follows = user.follower
        return render_template('follower.html',user=user,follows=follows)

@main.route('/<username>/followed/')
@login_required
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        follows = user.followed
        return render_template('followed.html',user=user,follows=follows)


@main.route('/edit-profile/',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditprofileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('信息修改成功！')
        return redirect(url_for('main.edit_profile'))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/all/')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed/')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp

@main.route('/delete/<int:post_id>/comments/<int:comment_id>/', methods=['GET','POST'])
@login_required
def deletecomments(post_id,comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('main.post', id=post_id))

@main.route('/map/')
@login_required
def walkroute():
    return render_template('map.html', begin=request.args.get('begin'), end=request.args.get('end'), way=request.args.get('way'))

@main.route('/travel/', methods=['GET','POST'])
@login_required
def travel():
    form = TravelForm()
    if form.validate_on_submit():
        return redirect(url_for('main.walkroute', begin=form.begin.data, end=form.end.data, way=form.way.data))
    return render_template('route.html', form=form)

