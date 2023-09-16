from flask import render_template
from app.poc import poc_bp as bp


@bp.route('/')
def index():
    # return '<h1>Neuromorphic Server Started Successfully...</h1>'
    return render_template('poc/index.html')