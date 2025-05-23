from flask import Flask, render_template, request, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/os')
def printos():
    user_agent = request.headers.get('User-Agent')
    return render_template_string(f"<h1>Welcome, your connection is from a {user_agent} based system.</h1>")

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(host="0.0.0.0", port=8000, debug=True)
=======
    app.run(debug=True)
>>>>>>> 04d729a (added service)
