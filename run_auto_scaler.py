from auto_scaler import app as auto_scaler_app

auto_scaler_app.run(
    '0.0.0.0',
    port=5001,
    debug=True
)