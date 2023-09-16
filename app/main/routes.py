from flask import render_template
from app.main import bp


@bp.route('/')
def index():
    # return '<h1>Neuromorphic Server Started Successfully...</h1>'
    return render_template('index.html')