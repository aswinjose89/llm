
from pathlib import Path
import openai, json, time
import pandas as pd
import tiktoken
from datetime import datetime, timedelta

openai.api_key ="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"


class Test:

    def get_gpt_schema(self):
        json_schema= {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Entity and Categories Response",
            "description": "A schema to validate the response containing entities with their types and categories.",
            "type": "object",
            "properties": {
                "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                    "text": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string"
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                        "type": "string"
                        },
                        "minItems": 1
                    }
                    },
                    "required": ["text", "type", "categories"],
                    "additionalProperties": False
                }
                }
            },
            "required": ["entities"],
            "additionalProperties": False
            }





        return json_schema
    
    def gpt4_response(self, instruction):        
        response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                            # {
                            # "role": "system",
                            # "content": "I have a document containing several sentences. Some parts of these sentences contain sensitive information pertaining to categories such as Military Affairs, Foreign Government Data, Intelligence Operations, U.S. Foreign Relations, National Security Science and Technology, Nuclear Security Programs, Security Infrastructure Vulnerabilities, and Weapons of Mass Destruction. Please replace only the specific words or phrases that fall under these categories with the name of the relevant category in brackets. Keep the original spelling and structure of the sentences intact, and do not alter non-sensitive parts of the text"
                            # },
                            {"role": "user", "content": instruction}              
                        ],
                    functions=[{"name": "getNer", "parameters": self.get_gpt_schema()}],
                    function_call={"name": "getNer"},
                max_tokens=4096)  
        import pdb;pdb.set_trace()
        return response

    def run(self):
        instruction=f"""            
        Given the sentence 'SAC OPERATION IN THE CUBAN MISSILE CRISIS OF 1962 HISTORICAL STUDY', 
        identify all entities and categorize them according to the following categories: 
        Military Plans, Weapons Systems, Military Operations, Date, Military Organisation, Destination, 
        Location, Military Affairs, Foreign Government Data, Intelligence Operations, U.S. Foreign Relations, 
        National Security Science and Technology, Nuclear Security Programs, Security Infrastructure Vulnerabilities, and Weapons of Mass Destruction. 
        Provide the output in JSON format, listing each entity with its type and matched categories         
        """
        response= self.gpt4_response(instruction)
        response= response.choices[0].message.function_call.arguments
        # response= response.strip()     
        response= json.loads(response)

Test().run()