
from flask import Flask, render_template, request
app = Flask(__name__)
@app.route('/user_profile')
def user_profile():
    # Simulate user-generated content
    user_input = request.args.get('user_input', '')
    
    return user_input

if __name__ == '__main__':
    app.run(debug=False)
