from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import EmailField, PasswordField
from wtforms.validators import DataRequired, NumberRange


class ExpenseForm(FlaskForm):
    category = SelectField('Category', choices = [('food', 'Food'), ('household', 'Household'),
                                                  ('internet', 'Internet'),('transport', 'Transport'),], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    date = DateField('Date', default=date.today())
    submit = SubmitField('Add Expense')

class IncomeForm(FlaskForm):
    source = SelectField('Source', choices = [('salary', 'Salary'), ('commission', 'Commission'),
                                                  ('bonus', 'Bonus'),('profit', 'Profit'),], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    date = DateField('Date', default=date.today())
    submit = SubmitField('Add Income')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

