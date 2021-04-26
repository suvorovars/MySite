from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ApplicationsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Идея")
    text = TextAreaField("Текст песни")
    feedback = TextAreaField("Контакты")
    submit = SubmitField('Отправить')
