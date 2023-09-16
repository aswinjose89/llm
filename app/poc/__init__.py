from flask import Blueprint

poc_bp = Blueprint('poc', __name__)

from app.poc import routes