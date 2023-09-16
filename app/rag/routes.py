from flask import render_template, request, jsonify
from app.rag import rag_bp as bp

#Local Class
from .api import API

@bp.route('/')
def index():
    return render_template('rag/index.html')

# @bp.route('/test_api', methods=['GET'])
# def test_api():
#     name = request.args.get('name')
#     resp= {'status': 'Api working'}
#     return jsonify(resp)

# @bp.route('/snn_predict', methods=['POST'])
# def snn_predict():
#     return API().post__predict_api(request)

# @bp.route('/snn_feature_count', methods=['POST'])
# def snn_feature_count():
#     return API().post__model_feature_count(request)