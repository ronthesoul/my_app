from flask import Flask, render_template, request, render_template_string


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/os")
def printos():
    user_agent = request.headers.get("User-Agent")
    # keep line short; let Jinja inject the value
    return render_template_string(
        "<h1>Welcome, your connection is from a {{ ua }} based system.</h1>",
        ua=user_agent,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)





