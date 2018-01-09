from flask import Flask
from flask import render_template, send_from_directory
from flask import jsonify

app = Flask(__name__, static_url_path='')

from config import Config

application_config = {
    0: Config(True, 100)
}


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
def create_new():
    pass


@app.route('/admin/<int:id>')
def manage_experiment(id):
    pass


@app.route('/admin/')
def admin_panel():
    return render_template('admin.html')


@app.route('/experiment/<int:id>')
def hello_world(id):
    return render_template('index.html')


@app.route('/experiment/<int:id>/config')
def experiment_config(id):
    return jsonify(application_config[id].dict())

app.run(host='0.0.0.0')