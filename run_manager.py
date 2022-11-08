from manager_app import app as manager_app

manager_app.run(
    '0.0.0.0',
    port=5002,
    debug=True
)