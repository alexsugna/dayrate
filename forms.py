from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional
from wtforms import validators
import formats

class OptionalIfFieldEqualTo(Optional):
    # modified from https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
    def __init__(self, other_field_name, value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        super(OptionalIfFieldEqualTo, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data == self.value:
            super(OptionalIfFieldEqualTo, self).__call__(form, field)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    reenter_password = PasswordField('Re-Enter Password', validators=[DataRequired()])
    submit = SubmitField('Create Account')

class PickDayForm(FlaskForm):
    day = DateField('Day', format=formats.date, validators=[OptionalIfFieldEqualTo('today', value=True)])
    today = BooleanField('Today')
    submit = SubmitField('Choose Day')

class DayRateForm(FlaskForm):
    rating = FloatField('Rating', validators=None)
    comments = TextAreaField('Comments', validators=[validators.length(max=200)])
    submit = SubmitField('Save Rating Details')

class CreateGroup(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired()])
    include_user = BooleanField('Include yourself in Group')
    submit = SubmitField('Create Group')

class AddUserToGroupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Add User')

class ChangeGroupOwnerForm(FlaskForm):
    new_owner = SelectField('New Owner', choices=None, validators=[DataRequired()])
    submit = SubmitField('Change Owner')

class DeleteGroupForm(FlaskForm):
    submit = SubmitField('Permanently Delete Group')
