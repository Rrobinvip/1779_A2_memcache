from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
# from wtforms import StringField, SubmitField, FileField
from wtforms.fields import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from frontend import app

'''
This module gives all forms needed for every pages. Forms are written in classes to acquire decent ability on expension.
'''

class ConfigForm(FlaskForm):
    size = IntegerField(
        "size",
        validators=[
            DataRequired(),
            NumberRange(min=1, max=1024)
        ],
        render_kw={"placeholder": "Size ~MB"}
    )
    replacement_policy = SelectField(
        "replacement_policy",
        choices=[(1, "Drop least use"), (2, "Random drop")]
    )
    submit = SubmitField("Apply")

class ManualForm(FlaskForm):
    growing = SubmitField("Growing")
    shrinking = SubmitField("Shrinking")
    refresh = SubmitField("Refresh status")

class ClearForm(FlaskForm):
    clear = SubmitField("Clear Memcache")

class DeleteForm(FlaskForm):
    delete = SubmitField("Delete all data")

