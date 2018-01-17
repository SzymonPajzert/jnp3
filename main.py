from functools import wraps

from flask import Flask, redirect, request, current_app
from flask import jsonify
from flask import render_template, send_from_directory
from flask_login import LoginManager, login_user, login_required
from flask_login.utils import current_user

from experiment.models import User
from experiment.util import random_bool
from experiment.user import SignupForm
from experiment.database import db_session, init_db

app = Flask(__name__, static_url_path='')
app.secret_key = 'sekretnamyszkaagatka'

login_manager = LoginManager()
login_manager.init_app(app)

# TODO remove
init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not (current_user.is_authenticated and current_user.is_admin):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


""" TODO move to models 
experiments = {
    0: Experiment(Config(True, 100, 6))
}
"""


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/new/')
@admin_required
def create_new():
    pass


@app.route('/admin/<string:id>')
@admin_required
def manage_user(id):
    pass


@app.route('/admin/')
@admin_required
def admin_panel():
    return render_template('admin.html')


@app.route('/experiment/<int:id>')
@login_required
def hello_world(id):
    return render_template('index.html')


@app.route('/experiment/<int:id>/config')
@login_required
def experiment_config(id):
    return jsonify(experiments[id].config.dict())


@app.route('/experiment/<int:id>/data')
@login_required
def experiment_data(id):
    if experiments[id].current:
        return jsonify(experiments[id].current)
    else:
        return experiment_data_new(id)


@app.route('/experiment/<int:id>/data/new')
@login_required
def experiment_data_new(id):
    experiments[id].current = random_bool(experiments[id].config.size)
    return jsonify(experiments[id].current)


@app.route('/')
def root():
    if current_user.is_authenticated:
        return redirect('/experiment/1')
    else:
        return redirect('/signup')


@app.route('/signup', methods=['GET', 'POST'])
def register():
    print(User.query.all())

    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():

            user_id = form.email.data
            user_not_found = User.query.filter(User.id == user_id).count() == 0

            if user_not_found:
                user = User(form.email.data, form.password.data)
                db_session.add(user)
                db_session.commit()
                print(User.query.all())

                return "User created"
            else:
                return "User with username already exists"
        else:
            return "Form didn't validate"


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(User.query.all())

    form = SignupForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():

            user_id = form.email.data
            user_found = User.query.filter(User.id == user_id).count() != 0

            if user_found:
                user = User.query.filter(User.id == user_id).first()

                if user.password == form.password.data:
                    login_user(user)
                    return "User logged in"
                else:
                    return "Wrong password"
            else:
                return "user doesn't exist"
    else:
        return "form not validated"


if __name__ == '__main__':
    app.run(host='0.0.0.0')