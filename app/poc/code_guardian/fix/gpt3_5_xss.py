from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/user_profile')
def user_profile():
    user_input = request.args.get('user_input', '')
    # Perform input validation to prevent code injection
    user_input = user_input.replace('<', '&lt;').replace('>', '&gt;')
    return user_input

if __name__ == '__main__':
    app.run(debug=False)