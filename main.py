#main.py
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session
import forms
from db import validate_login, validate_account_creation, day_info
import db
from config import Config
import formats
import flask
import stats
from urllib.parse import quote_plus

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

@app.route('/dash_data', methods=["GET", "POST"])
def dash_data():
    check_login()
    dash_info = db.get_dash_info(session['username'])
    days = []
    ratings = []
    for rating in dash_info:
        days.append(rating[0])
        ratings.append(rating[1])
    data = { "x" : days, "y" : ratings}
    return data

@app.route('/day_info_link', methods=['GET', 'POST'])
def day_info_link():
    check_login()
    day = request.args.get('day')
    day_information = day_info(day, session['username'])
    try:
        del day_information['_id']
    except KeyError:
        pass
    session['day_information'] = day_information
    return redirect('day_info')


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
        groups.append((quote_plus(group['name']), group['name']))
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

@app.route('/display_group', methods=['POST', 'GET'])
def display_group(): # this process needs validation/feedback
    check_login()
    group_name = request.args.get('group_name')
    group_data = db.get_group_data(session['username'], group_name)
    if len(group_data) < 1:
        return redirect('/groups')
    group_data = group_data[0]
    group_users = group_data['users']
    owner = False
    owner_username = group_data['owner']
    if owner_username == session['username']:
        owner = True
    encoded = (quote_plus(group_name), quote_plus(owner_username))
    return render_template("group_display.html", title=group_name, group_users=group_users,
                           group_name=group_name, owner=owner, encoded=encoded)

@app.route('/group_dash', methods=['POST', 'GET'])
def group_dash(): # this process needs validation/feedback
    """
    NEEDS A LOT OF WORK :)
    """
    group_name = request.args.get('group_name')
    group_data = db.get_group_data(session['username'], group_name)#[0]
    group_users = group_data[0]['users']
    group_dash_info = []
    for username in group_users:
        group_dash_info.append((username, db.get_dash_info(username)))
    return render_template("group_dash.html", title="{} Dashboard".format(group_name),
                           group_dash_info=group_dash_info, group_name=group_name,
                           group_name_encoded=quote_plus(group_name))

@app.route('/group_dash_data', methods=['POST', 'GET'])
def group_dash_data():
    check_login()
    group_name = request.args.get('group_name')
    dash_info = db.get_group_dash_data()
    days = []
    ratings = []
    for rating in dash_info:
        days.append(rating[0])
        ratings.append(rating[1])
    data = { "x" : days, "y" : ratings}
    return data


@app.route('/add_user_to_group', methods=['POST', 'GET'])
def add_user_to_group():
    check_login()
    form = forms.AddUserToGroupForm()
    group_name = request.args.get('group_name')
    if form.validate_on_submit():
        username_to_add = form.username.data
        if len(db.find_user(username_to_add)) >= 1:
            insert_result, feedback, _ = db.insert_user_to_group(username_to_add, group_name, session['username'])
            flash(feedback)
            if insert_result:
                return redirect("/display_group?group_name={}".format(quote_plus(group_name)))
            return render_template('add_user_to_group.html', form=form, group_name=group_name)
        flash("Username not found :(")
    return render_template('add_user_to_group.html', form=form, group_name=group_name)


@app.route('/change_group_owner', methods=['POST', 'GET'])
def change_group_owner():
    check_login()
    group_name = request.args.get('group_name')
    user_list = db.get_group_data(session['username'], group_name)[0]['users']
    form = forms.ChangeGroupOwnerForm()
    form.new_owner.choices = user_list
    if form.validate_on_submit():
        new_owner = form.new_owner.data
        if len(db.find_user(new_owner)) >= 1:
            current_owner = request.args.get('current_owner')
            update_result, feedback, _ = db.change_group_owner(current_owner, new_owner, group_name)
            flash(feedback)
            if update_result:
                return redirect("/display_group?group_name={}".format(quote_plus(group_name)))
    return render_template('change_group_owner.html', form=form, group_name=group_name, user_list=user_list)


@app.route('/delete_group', methods=['POST', 'GET'])
def delete_group():
    check_login()
    group_name = request.args.get('group_name')
    delete_form = forms.DeleteGroupForm()
    if delete_form.validate_on_submit():
        username = session['username']
        if username == db.get_group_data(username, group_name)[0]['owner']:
            delete_result, feedback, _ = db.delete_group(username, group_name)
            flash(feedback)
            if delete_result:
                return redirect("/display_group?group_name={}".format(quote_plus(group_name)))
    return render_template('delete_group.html', form=delete_form, group_name=group_name)


def check_login():
    if 'username' in session:
        return
    else:
        return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)
