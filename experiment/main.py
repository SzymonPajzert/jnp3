from functools import wraps

from flask import Flask, redirect, request, current_app
from flask import jsonify
from flask import render_template, send_from_directory
from flask_login import LoginManager, login_user, login_required
from flask_login.utils import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired

from experiment.models import User, Experiment, Config
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
        print(current_user)
        print(current_user.is_authenticated)
        print(current_user.is_admin)
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not (current_user.is_authenticated and current_user.is_admin):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter(User.id == user_id).first()

    if user:
        return user.login_model()
    else:
        return None


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
    config = Config(True, 0, 10, 3)
    e = Experiment(config)

    db_session.add(e)
    db_session.commit()

    return redirect('/experiment/{}'.format(e.id))


@app.route('/admin/')
@admin_required
def admin_panel():
    return render_template('admin.html')


class ExperimentConfigForm(FlaskForm):
    feedback = BooleanField('feedback')
    delay = IntegerField('delay', validators=[DataRequired()])
    size = IntegerField('size', validators=[DataRequired()])
    training_size = IntegerField('training_size', validators=[DataRequired()])
    submit = SubmitField("Sign In")


@app.route('/admin/<int:id>', methods=['GET', 'POST'])
@admin_required
def experiment_admin_panel(id):
    form = ExperimentConfigForm()
    experiment = Experiment.query.get(id)

    if request.method == 'GET':
        return render_template('exp_admin.html', form=form, experiment=experiment)
    elif request.method == 'POST':
        if form.validate_on_submit():

            config = Config(
                form.feedback.data,
                form.delay.data,
                form.size.data,
                form.training_size.data)

            Experiment.query.filter_by(id=id).update({'config': config})
            db_session.commit()

            return redirect('/experiment/{}'.format(id))
    else:
        return "form not validated"




@app.route('/experiment/<int:id>')
@login_required
def hello_world(id):
    return render_template('index.html')


@app.route('/experiment/<int:id>/config')
@login_required
def experiment_config(id):
    return Experiment.query.get(id).config.dict()


@app.route('/experiment/<int:id>/data', methods=['GET'])
@login_required
def experiment_data(id):
    experiment = Experiment.query.get(id)

    if experiment.current:
        return jsonify(experiment.current)
    else:
        return experiment_data_new(id)


@app.route('/experiment/<int:id>/data/new', methods=['POST'])
@login_required
def experiment_data_new(id):
    time = request.json['time']
    print('Time == {}'.format(time))

    experiment = db_session.query(Experiment).get(id)
    print(experiment)
    print(experiment.times)

    if (experiment.current is not None) and time > 0:
        # we don't add times if they're are unimportant

        prev_times = experiment.times.get(experiment.current, list())
        prev_times.append(time)
        experiment.times[experiment.current] = prev_times
        Experiment.query.filter_by(id=id).update({'times': experiment.times})
        db_session.commit()

    if len(experiment.times) < experiment.config.training_size:
        print("Generating new")
        # add new pattern to the pool
        experiment.current = random_bool(experiment.config.size)
    else:
        print("Reusing old")
        # we choose one that was least used
        pairs = [(pair[0], len(pair[1])) for pair in experiment.times.items()]
        experiment.current = sorted(pairs, key=lambda pair: pair[1])[0][0]

    db_session.commit()

    return jsonify(experiment.current)


@app.route('/')
def root():
    if current_user.is_authenticated:
        return redirect('/experiment/0/')
    else:
        return redirect('/signup')


@app.route('/signup', methods=['GET', 'POST'])
def register():
    print(Experiment.query.all())
    print('Users: {}'.format(User.query.all()))

    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():

            user_id = form.email.data
            user_not_found = User.query.filter(User.id == user_id).count() == 0

            if user_not_found:
                user = User(form.email.data, form.password.data)
                print(user)

                db_session.add(user)
                db_session.commit()

                login_user(user.login_model())

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
                    login_user(user.login_model())
                    return "User logged in"
                else:
                    return "Wrong password"
            else:
                return "user doesn't exist"
    else:
        return "form not validated"


if __name__ == '__main__':
    app.run(host='0.0.0.0')