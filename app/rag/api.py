
import json
import numpy as np

#Local Class
from .controller import Akida

"""
Maintain all the api request and each function name prefix with API method(GET/POST)
"""
class API:
    def return_error(err_str):
        return {
            "status": 1,
            "data": err_str
        }
    def post__model_feature_count(self, request):
        if not request.data: return API.return_error("Error: Request payload must be provided.")
        print(request.data)
        record : dict = json.loads(request.data) 
        model_name= record.get("model_name", None)
        if not model_name: return API.return_error("Error: Model name not provided.")
        
        try:
            ret_val = 0
            ret_data = Akida().get_model_feature_count(model_name)
            return {
                "status": ret_val,
                "data": ret_data
            }
        except Exception as e:
            return API.return_error("Error: " + str(e))
    
    def post__predict_api(self, request):
        if not request.data: return API.return_error("Error: Request payload must be provided.")
            
        record : dict = json.loads(request.data) 
        model_name= record.get("model_name", None)
        input_data = record.get("input_data", None)
        if not model_name: return API.return_error("Error: Model name not provided.")
        if not input_data: return API.return_error("Error: Input data not provided.")
        
        try:
            pred= Akida().get_predictions(input_data, model_name)
            ret_val = 0
            return {
                "status": ret_val,
                "data": pred
            }
        except Exception as e:
            return API.return_error("Error: " + str(e))