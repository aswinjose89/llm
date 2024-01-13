
import openai

openai.api_key = "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"

# confirm authentication was successful
openai.Engine.list()['data'][0]



# from IPython.display import HTML

# def page_builder(title: str, copy_text: str):
#     """Takes title and copy text to create a product page in simple HTML
#     """
#     html = """

    
#         Awesome Product
        
    
    
        
#             """+title+"""
#             """+copy_text+"""
        
    
# """
#     with open('index.html', 'w') as fp:
#         fp.write(html)
#     return HTML(filename='index.html')


# page_builder(
#     title="Awesome Product",
#     copy_text="Not very good copy text (it was written by a human)."
# )



page_builder_func = {
    "name": "page_builder",
    "description": "Creates product web pages",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The name of the product"
            },
            "copy_text": {
                "type": "string",
                "description": "Marketing copy that describes and sells the product"
            }
        },
        "required": ["title", "copy_text"]
    }
}


prompt = "Create a web page for a new cutting edge mango cutting machine"

res = openai.ChatCompletion.create(
    model='gpt-4',  # swap for gpt-3.5-turbo-0613 if needed
    messages=[{"role": "user", "content": prompt}],
    functions=[page_builder_func]
)

if res['choices'][0]["finish_reason"] == "function_call":
    print("We should call a function!")


import json
import pdb;pdb.set_trace()
name = res['choices'][0]['message']['function_call']['name']
args = json.loads(res['choices'][0]['message']['function_call']['arguments'])
name, args
