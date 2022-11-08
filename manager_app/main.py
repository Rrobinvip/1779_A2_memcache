from manager_app import app

@app.route("/")
def hello_world():
    return "<p>Hello, World! manager</p>"