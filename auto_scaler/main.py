from auto_scaler import app

@app.route("/")
def hello_world():
    return "<p>Hello, World! scaler</p>"