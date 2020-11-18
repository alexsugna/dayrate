#main.py
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session
import forms
from db import validate_login, validate_account_creation, day_info
import db
from config import Config
import formats
import flask
import stats

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = b'48hf9j98rfh_+==_98j9i'

@app.route('/', methods=['POST','GET'])
def home():
    check_login()
    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        success, feedback, _id = validate_login(form.username.data, form.password.data)
        flash(feedback)
        if success:
            session['username'] = form.username.data
            return redirect("/")
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout', methods=['POST','GET'])
def logout():
    check_login()
    session.pop('username', None)
    return redirect("/")

@app.route('/create_account', methods=['POST','GET'])
def create_account():
    form = forms.CreateAccountForm()
    if form.validate_on_submit():
        success, feedback = validate_account_creation(form.username.data,
                                             form.password.data,
                                             form.reenter_password.data)
        flash(feedback)
        if success:
            session['username'] = form.username.data
            return redirect("/")
    return render_template('create_account.html', title="Create Account", form=form)


@app.route('/dash', methods=['POST','GET'])
def dash():
    check_login()
    username = session['username']
    dash_info = db.get_dash_info(username)
    dash_stats = stats.stat_summary(username, 100)
    return render_template('dash.html', title="{}'s Dashboard".format(username),
                           dash_info=dash_info, dash_stats=dash_stats)


@app.route('/day_info', methods=['GET', 'POST'])
def day_info_get():
    check_login()
    day_info = session['day_information']
    day_rate_form = forms.DayRateForm()
    if flask.request.method == 'GET':
        day_rate_form.comments.data = day_info['comments']
        return render_template("day_info.html", title="Day Details",
                                day_information=day_info, form=day_rate_form)
    else:
        session.pop('day_information', None)
        if day_rate_form.validate_on_submit():
            day_info = formats.fill_day_info(day_rate_form, day_info["day"], session['username'])
            result, feedback, id = db.save_dayrate(day_info, session['username'])
            flash(feedback)
            return redirect("/dash")
        return render_template("day_info.html", title="Day Details",
                                day_information=day_info, form=day_rate_form)

@app.route('/pick_day', methods=['POST', 'GET'])
def pick_day():
    check_login()
    form = forms.PickDayForm()
    if form.validate_on_submit():
        if form.today.data:
            day = db.get_today()
        else:
            day = str(form.day.data)
        day_information = day_info(day, session['username'])
        if day_information is None:
            day_information = formats.day_information
            day_information['day'] = day
        try:
            del day_information['_id']
        except KeyError:
            pass
        session['day_information'] = day_information
        return redirect('day_info')
    return render_template('pick_day.html', title="Pick a Day to Rate", form=form)

@app.route('/groups', methods=['POST', 'GET'])
def groups():
    check_login()
    username = session['username']
    my_groups = db.get_my_groups(username)
    groups = []
    for group in my_groups:
        groups.append(group['name'])
    return render_template('groups.html', title="{}'s Groups".format(username),
                           groups=groups)

@app.route('/create_group', methods=['POST', 'GET'])
def create_group():
    check_login()
    form = forms.CreateGroup()
    if form.validate_on_submit():
        result, feedback, id = db.create_group(form.name.data, session['username'], form.include_user.data)
        flash(feedback)
        return redirect("/groups")
    return render_template('create_group.html', title="Create Group", form=form)

def check_login():
    if 'username' in session:
        return
    else:
        return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)
