from functools import wraps
from random import shuffle
import json

from flask import Flask, redirect, request, current_app
from flask import jsonify
from flask import render_template, send_from_directory
from flask_login.utils import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired

from experiment.database import db_session, init_db
from experiment.models import Experiment, Quiz, ExperimentConfig
from experiment.user import SignupForm
from experiment.util import random_bool

app = Flask(__name__, static_url_path='')
app.secret_key = 'sekretnamyszkaagatka'

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


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

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
            pass
            # TODO

    else:
        return "form not validated"

def getExperiment(id):
    result = db_session.query(Experiment).get(id)
    print("Asking for: {}".format(result))
    return result

@app.route('/experiment/<int:id>/', methods=['GET'])
def experiment_route(id):
    experiment = getExperiment(id)

    print(experiment)

    stage = experiment.results.current_stage
    config = db_session.query(ExperimentConfig).get(experiment.config)


    if stage < 5:
        context = {
            'stage': stage,
            'executionTime': config.execution[stage],
            'startMessage': config.message[stage],
            'showAlert': "true",
        }
    else:
        context = {}

    if stage in [1, 2]:
        return render_template('gil.html', **context)
    elif stage in [3, 4]:
        if stage == 4:
            print(experiment.results.quiz_order)
            print(experiment.results.current_quiz)

            quiz_id = experiment.results.quiz_order[experiment.results.current_quiz]

            if experiment.results.current_quiz > 0:
                # don't show alert
                context['showAlert'] = "false"

            print('current quiz: {}'.format(quiz_id))

            print(db_session.query(Quiz).count())

            quiz = Quiz.query.get(quiz_id)

            print(quiz)

            context['description'] = quiz.description
            context['description_short'] = quiz.description_short
            context['goal'] = quiz.goal
            context['answers'] = [quiz.premise, quiz.not_premise, quiz.conclusion, quiz.not_conclusion]
            shuffle(context['answers'])

        else:
            context['answers'] = [''] * 4

        return render_template('embed_example.html', **context)
    else:
        return "Koniec"

@app.route('/experiment/<int:id>/next', methods=['GET', 'POST'])
def increase_counter(id):
    experiment = getExperiment(id)

    stage = experiment.results.current_stage
    if stage == 4:
        results = experiment.results
        results.current_quiz += 1

        if results.current_quiz == len(results.quiz_order):
            results.current_stage += 1

        print('next: {}', results)

        Experiment.query.filter_by(id=id).update({'results': results})
        db_session.commit()

        return "Ok"

    else:
        return "Bad request"


@app.route('/experiment/<int:id>/<int:stage>', methods=['PUT'])
def experiment_put_results(id, stage):
    experiment = getExperiment(id)

    if experiment.results.current_stage == stage:
        data = request.json
        print(data)

        new_results = experiment.results.digest_data(data)

        if new_results:
            Experiment.query.filter_by(id=id).update({'results': new_results})
            db_session.commit()

            # we managed to parse the data
            return "Ok"
        else:
            return "Unable to parse the data"

    else:
        return "Results sent for the wrong stage"

@app.route('/export', methods=['GET', 'POST'])
def export():
    result = [['experiment', 'stage', 'question', 'time', 'event', 'id']]

    for experiment in Experiment.query:
        print(json.dumps(experiment.json()))

        times = experiment.results.result_times

        print(times)

        eid = experiment.id

        for key in times.keys():
            if key == 4:

                for question in times[key].keys():
                    for time in times[key][question]["answer"]:
                      result.append([eid, key, question, time['time'], 'answer', time['id']])

                    for time in times[key][question]["click"]:
                        result.append([eid, key, question, time, 'click', -1])

            else:
                for time in times[key]["answer"]:
                    result.append([eid, key, -1, time['time'], 'answer', time['id']])

                for time in times[key]["click"]:
                    result.append([eid, key, -1, time, 'click', -1])

    with open('export.csv', 'w') as output_file:
        print("Dumping")
        for row in result:
            for cell in row:
                output_file.write("{},".format(cell))

            output_file.write('\n')

    return "Ok"


@app.route('/experiment/<int:id>/data/new', methods=['POST'])
def experiment_data_new(id):
    time = request.json['time']
    print('Time == {}'.format(time))

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
        return redirect('/admin/')
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = SignupForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            experiment = Experiment(form.pseudonim.data, form.sex.data == "woman", form.wiek.data)
            db_session.add(experiment)
            db_session.commit()

            return redirect("experiment/{}".format(experiment.id))
        else:
            return "form not validated"
    else:
        return "Wrong request"


if __name__ == '__main__':
    app.run(host='0.0.0.0')