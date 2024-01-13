import openai

schema = {
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
      "type": "string",
      "description": "Details of the CWE ID, base findings, attack surface, and environment for the identified vulnerabilities."
    },
    "nvd": {
      "type": "string",
      "description": "Standard metadata from the NVD related to the identified vulnerabilities."
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
      "type": "string",
      "description": "Test cases applicable for mitigating vulnerabilities in the code."
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



import os
import openai

openai.api_key = "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"
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
completion = openai.ChatCompletion.create(
  model="gpt-4-1106-preview",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f" Find the source code vulnerability with fixes for given Vulnerable source code snippet {vulnerable_code()}"}
  ],
  functions=[{"name": "set_vulnerability_fix", "parameters": schema}],
  function_call={"name": "set_vulnerability_fix"},
  temperature=0,
)

print(completion.choices[0].message.function_call.arguments)