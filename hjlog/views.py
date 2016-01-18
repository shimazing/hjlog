from hjlog import app, db, lm
from flask import render_template, redirect, request, url_for, flash, jsonify
from werkzeug import secure_filename
from sqlalchemy import desc
from .models import Post, Photo, Tag, User
from .forms import PostForm, PhotoForm, LoginForm
from flask.ext.login import login_user, logout_user, current_user
import os

# Login
@lm.user_loader
def load_user(user_id):
    u = None
    try:
        u = User.query.filter_by(id=user_id).one()
    except:
        pass

    return u

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first_or_404()
        except:
            flash('등록된 관리자가 아닙니다 :(', 'warning')
            return redirect(url_for('login'))

        if user.is_correct_password(form.password.data):
            login_user(user)
            flash('관리자님 환영합니다 :)', 'success')
            return redirect(url_for('about'))
        else:
            flash('올바르지 않은 ID/PW 쌍입니다 :-(', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('성공적으로 로그아웃 되었습니다 :)', 'success')

    return redirect(url_for('about'))

# 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404), 404

# 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', code=500), 500

# About
@app.route('/')
def about():
    return render_template('about.html')

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Blog
@app.route('/posts/<category>/<page>')
def posts(category, page):
    pgn = Post.query.filter_by(category=category).order_by(desc(Post.datetime))\
            .paginate(int(page), per_page = 10)
    return render_template('posts.html', posts = pgn.items, c = category, pgn = pgn)

@app.route('/post/<id>')
def post(id):
    post = Post.query.filter_by(id=id).one()
    return render_template('post.html', post=post)

@app.route('/post/new', methods=['GET', 'POST'])
def post_new():
    form = PostForm()
    if request.method=='POST':
        if form.validate_on_submit():
            title, body, category, author, tag_names = request.form.get('title'), request.form.get('body'), \
                    request.form.get('category'), current_user, request.form.get('tags')

            # Tagging
            tag_names = [tag_name.strip('\n').strip(' ') for tag_name in tag_names.split(',')]
            if tag_names == ['']:
                tag_names = []

            tags = []
            for tag_name in tag_names:
                try:
                    t = Tag(tag_name)
                    db.session.add(t)
                    db.session.commit()
                except:
                    db.session.rollback()
                    t = Tag.query.filter_by(tag_name = tag_name).one()
                finally:
                    tags.append(t)

            post = Post(title, body, category, author, tags)

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('post', id=post.id))
        else:
            flash('이런, 뭔가 빼먹으신 모양인데요?', 'warning')
            return render_template('post_new.html', form=form)

    return render_template('post_new.html', form=form)

@app.route('/post/<id>/delete')
def post_delete(id):
    post = Post.query.filter_by(id=id).one()
    db.session.delete(post)
    db.session.commit()
    flash('성공적으로 삭제되었습니다 :)', 'success')
    return redirect(url_for('posts', category='daily', page=1))

@app.route('/post/<id>/edit', methods=['GET', 'POST'])
def post_edit(id):
    post = Post.query.filter_by(id=id).one()

    tags_str = ", ".join([tag.tag_name for tag in post.tags])

    form = PostForm(title = post.title, body = post.body, tags=tags_str,
            category=post.category)

    if request.method == 'POST':
        if form.validate_on_submit():
            title, body, category, tag_names = request.form.get('title'), request.form.get('body'), \
                    request.form.get('category'), request.form.get('tags')

            # Tagging
            tag_names = [tag_name.strip('\n').strip(' ') for tag_name in tag_names.split(',')]
            if tag_names == ['']:
                tag_names = []

            tags = []
            for tag_name in tag_names:
                try:
                    t = Tag(tag_name)
                    db.session.add(t)
                    db.session.commit()
                except:
                    db.session.rollback()
                    t = Tag.query.filter_by(tag_name = tag_name).one()
                finally:
                    tags.append(t)

            post.title, post.body, post.category, post.tags = title, body, category, tags

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('post', id=post.id))
        else:
            flash('이런, 뭔가 빼먹으신 모양인데요?', 'warning')
            return render_template('post_edit.html', form=form, id=post.id)

    return render_template('post_edit.html', form=form, id=post.id)

@app.route('/photoajax', methods=['POST'])
def photo_ajax():
    if request.method == 'POST':
        print(request.files)
        photo = request.files['file']
        print(photo)
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            directory=url_for('static', filename='image/photo/'+filename)
            return jsonify(name=filename, direc=directory)

# Photo
@app.route('/photo')
def photo():
    photos = Photo.query.order_by(desc(Photo.datetime)).all()
    return render_template('photo.html', photos=photos)

#@app.route('/photo/add', methods=['GET', 'POST'])
#def photo_add():
#    form = PhotoForm()
#    if request.method == 'POST':
#        if form.validate_on_submit():
#            title, description = request.form.get('title'), request.form.get('description')
#            uploaded_file = request.files['photo']
#
#            if allowed_file(uploaded_file.filename):
#                filename = secure_filename(uploaded_file.filename)
#                uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#            else:
#                flash("올바른 사진 파일이 아닙니다 -_-", 'danger')
#                return redirect(url_for('photo_add'))
#
#            photo = Photo(title, description, filename, 28)
#
#            db.session.add(photo)
#            db.session.commit()
#            return redirect(url_for('photo'))
#        else:
#            flash('이런, 뭔가 빼먹으신 모양인데요?', 'warning')
#            return render_template('photo_add.html', form=form)
#
#    return render_template('photo_add.html', form=form)
