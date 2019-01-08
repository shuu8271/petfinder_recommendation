from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, Length


class SelectionForm(FlaskForm):
    selection1 = IntegerField('Selection #1', validators=[DataRequired(), Length(min=6, max=12)])
    selection2 = IntegerField('Selection #2')
    selection3 = IntegerField('Selection #3')
    selection4 = IntegerField('Selection #4')
    selection5 = IntegerField('Selection #5')
    submit = SubmitField('Submit selections')
