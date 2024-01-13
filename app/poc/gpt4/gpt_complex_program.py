import openai
from rich import print
openai.api_key = "Put Your API Key here"

def vulnerable_code():
    code= """
    from flask import Flask, render_template, request
    app = Flask(__name__)
    @app.route('/user_profile')
    def user_profile():
        # Simulate user-generated content
        user_input = request.args.get('user_input', '')
        return user_input

    if __name__ == '__main__':
        app.run(debug=False)
    """
    return code

class GPT4Program:
    def __init__(self) -> None:
        self.model= "gpt-4-1106-preview"
    
    def get_cybersecurity_schema(self):
        json_schema= {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "The identifier of the model to be used."
                },
                "programming_language": {
                    "type": "string",
                    "description": "The programming language of the vulnerable source code."
                },
                "compiler_name": {
                    "type": "string",
                    "description": "The name of the compiler used to compile the patched code."
                },
                "fixed_source_code": {
                    "type": "string",
                    "description": "The fixed source code, patched to address vulnerabilities according to CWE and NVD, and ready for building."
                },
                "software_packages": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of all the imported libraries or packages used in the source code."
                },
                "supporting_operating_system": {
                    "type": "string",
                    "description": "The supporting operating system(s) for the code, or 'cross-platform' if applicable."
                },
                "executive_summary": {
                    "type": "string",
                    "description": "A detailed description of the vulnerabilities in the code, their fixes, and any relevant analysis including discovery, exploitation, and social engineering aspects."
                },
                "vulnerability_details": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                        "vulnerability_id": {
                            "type": "string",
                            "description": "The ID of the vulnerability from the NVD."
                        },
                        "description": {
                            "type": "string",
                            "description": "A description of the identified vulnerability."
                        },
                        "severity": {
                            "type": "string",
                            "description": "The severity of the vulnerability."
                        },
                        "impact": {
                            "type": "string",
                            "description": "The impact of the vulnerability."
                        },
                        "recommendation": {
                            "type": "string",
                            "description": "Recommendations to avoid exploitation of the vulnerability."
                        },
                        "cvss_score": {
                            "type": "number",
                            "description": "The CVSS score of the vulnerability."
                        }
                        },
                        "required": ["vulnerability_id", "description", "severity", "impact", "recommendation", "cvss_score"]
                    },
                    "description": "Details of each identified vulnerability."
                },
                "vulnerability_type": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of types of vulnerabilities identified in the code."
                },
                "cwe": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of all applicable CWE identifiers for the vulnerabilities found in the provided source code. A brief description of each identified vulnerability corresponding to its CWE identifier."
                },
                "literature_survey": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "References to related literature survey articles."
                },
                "static_code_analysis": {
                    "type": "string",
                    "description": "Results from static code analysis tools, detailing code errors."
                },
                "coding_standard_violations": {
                    "type": "string",
                    "description": "Details of any coding standard violations found, or 'None' if no violations are present."
                },
                "test_cases": {
                    "type": "array",
                    "description": "list of testcases with steps to mitigating vulnerabilities in the source code",
                    "items": { "type": "string" }
                },
                "conclusion": {
                    "type": "string",
                    "description": "A concluding statement summarizing the critical vulnerabilities identified and the need for immediate action."
                },
                "user_role": {
                    "type": "string",
                    "description": "Role of the user making the request."
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "The maximum number of tokens to generate in the completion."
                },
                "temperature": {
                    "type": "number",
                    "description": "Controls randomness in generation. Higher is more random."
                }
            },
            "required": [
                "programming_language",
                "compiler_name",
                "fixed_source_code",
                "software_packages",
                "supporting_operating_system",
                "executive_summary",
                "vulnerability_details",
                "vulnerability_type",
                "cwe",
                "nvd",
                "literature_survey",
                "static_code_analysis",
                "coding_standard_violations",
                "test_cases",
                "conclusion",
                "model", "user_role", "max_tokens", "temperature"
            ]
            }
        return json_schema
    
    def run(self, vulnerable_code):     
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert cybersecurity penetration tester or analyzer"},
                {"role": "user", "content": f"Find the source code vulnerability with fixes for given Vulnerable source code snippet {vulnerable_code}"}
            ],
            functions=[{"name": "set_vulnerability_fix", "parameters": self.get_cybersecurity_schema()}],
            function_call={"name": "set_vulnerability_fix"},
            temperature=0,
        )
        response= completion.choices[0].message.function_call.arguments
        return response


inst= GPT4Program()
print(f"Sample Vulnerable Code is [bold blue]{vulnerable_code()}[/bold blue] \n Hit enter to process the given sample code to test")
while True:
    user_input = input("#Human: ")
    if not user_input:
        print('#Response: ',inst.run(vulnerable_code()))
    else:
        print('#Response: ',inst.run(user_input))
    