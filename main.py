#main.py
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session, make_response
import forms
from db import validate_login, validate_account_creation, day_info
import db
from config import Config
import formats
import flask
import stats
from urllib.parse import quote_plus             # function for encoding URL arguments
import datetime


app = Flask(__name__)
app.config.from_object(Config)                  # configure app for dev/testing/production


@app.route('/', methods=['POST','GET'])
def home():
    """
    Routes to and renders the homepage 'index.html'
    """
    return render_template('index.html', title="Home", dayrate_description=formats.dayrate_description)


@app.route('/login', methods=['POST','GET'])
def login():
    """
    Routes to and renders the homepage 'login.html'. If the user submits
    an invalid form, the login page is rendered again and the user is given
    feedback about what they did wrong.
    """
    form = forms.LoginForm()        # the login form
    if form.validate_on_submit():   # if the form is filled out correctly
        success, feedback, _id = validate_login(form.username.data, form.password.data) # validate the form information
        flash(feedback)             # flash validation feedback
        if success:                 # if information is valid
            session['username'] = form.username.data    # set username session variable to remember user
            return redirect("/")                        # redirect to homepage, this time logged in
    return render_template('login.html', title='Sign In', form=form)    # render login template if form is invalid or empty


@app.route('/logout', methods=['POST','GET'])
def logout():
    """
    Logs out the user and redirects to the homepage.
    """
    check_login()
    session.pop('username', None)   # remove username variable from session to log out user
    return redirect("/")


@app.route('/create_account', methods=['POST','GET'])
def create_account():
    """
    Renders create account form and validates new account information.
    """
    form = forms.CreateAccountForm()        # create account form
    if form.validate_on_submit():           # if form is valid
        success, feedback, _ = validate_account_creation(form.username.data,    # validate the create account form information
                                             form.password.data,
                                             form.reenter_password.data)
        flash(feedback)
        if success:
            session['username'] = form.username.data    # if account is valid, log in user
            return redirect("/")                        # redirect to the homepage
    return render_template('create_account.html', title="Create Account", form=form)    # render form again if invalid


@app.route('/dash', methods=['POST','GET'])
def dash():
    """
    Routes to user dashboard
    """
    check_login()                                                               # verify login
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    user_preferences = db.get_user_preferences(username)
    dash_info = db.get_dash_info(username)                                      # get user dashboard DayRates
    dash_stats = stats.stat_summary(username, user_preferences['num_ratings_stats'], user_preferences['stat_decimals']) # get user dashboard stats
    color_options = formats.color_options
    return render_template('dash.html', title="{}'s Dashboard".format(username),# render user dashboard template
                           dash_info=dash_info, dash_stats=dash_stats,
                           color_options=color_options)


@app.route('/dash_data', methods=["GET", "POST"])
def dash_data():
    """
    Handles ajax calls from dashboard for chart data. (This can probably be
    optimized at a later date.)
    """
    check_login()
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    dash_info = db.get_dash_info(username)                           # get ratings
    days = []                                                                   # x coords
    ratings = []                                                                # y coords
    for rating in dash_info:                                                    # iterate through ratings
        days.append(rating[0])                                                  # append day string to days list
    days.sort(key = lambda date: datetime.datetime.strptime(date, formats.date))# sort days chronologically
    """
    This portion iterates through the sorted days and finds the corresponding
    rating. It results in a rating list that maps one-to-one in order to the
    sorted day list.
    """
    for day in days:                                                            # iterate through days
        for rating in dash_info:                                                # iterate through ratings
            if rating[0] == day:                                                # if rating matches current day
                ratings.append(rating[1])                                       # append rating
    return { "x" : days, "y" : ratings }                                        # return json/dictionary of x and y data


@app.route('/day_info_link', methods=['GET', 'POST'])
def day_info_link():
    """
    Routes the DayRate links appearing on user dashboard to the rate a day form.
    """
    check_login()
    day = request.args.get('day')                                               # get url argument specifying day
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    day_information = day_info(day, username)                        # get the rating for that day (if it exists) using the database module
    try:                                                                        # try to delete the document id
        del day_information['_id']
    except KeyError:                                                            # if it throws a KeyError, then the document doesn't exist
        pass                                                                    # in this case day_info() returns a DayRate format without data
    session['day_information'] = day_information                                # include the day info as a session variable
    return redirect('day_info')                                                 # redirect to the rating handler


@app.route('/day_info', methods=['GET', 'POST'])
def day_info_get():
    """
    Routes to the DayRate form
    """
    check_login()
    day_info = session['day_information']                                       # get day_information from session variable
    day_rate_form = forms.DayRateForm()                                         # the DayRate form
    if flask.request.method == 'GET':                                           # if the request is a GET, this means we are requesting the form to fill out
        #day_rate_form.comments.data = day_info['comments']                      # set form comment data as session variable
        return render_template("day_info.html", title="Day Details",            # render DayRate template
                                day_information=day_info, form=day_rate_form)
    else:                                                                       # else the request is probably a POST (not a GET)
        session.pop('day_information', None)                                    # remove the rating info from the session variable
        if day_rate_form.validate_on_submit():                                  # if the form is valid
            try:
                username = session['username']                                              # define username variable
            except:
                return redirect('login')
            day_info = formats.fill_day_info(day_rate_form, day_info["day"], username)   # with the rating session info, populate a DayRate formatted object
            result, feedback, id = db.save_dayrate(day_info, session['username'])   # save the dayrate object in the database
            flash(feedback)
            return redirect("/dash")                                            # redirect to the user dashboard
        return render_template("day_info.html", title="Day Details",            # if the form is invalid, let the user try again
                                day_information=day_info, form=day_rate_form)


@app.route('/pick_day', methods=['POST', 'GET'])
def pick_day():
    """
    Renders the form for specifying the day to create a rating for
    """
    check_login()
    form = forms.PickDayForm()                                                  # choose a day form
    if form.validate_on_submit():
        day = str(form.day.data)                                            # else get the date the user input
        try:
            username = session['username']                                              # define username variable
        except:
            return redirect('login')
        day_information = day_info(day, username)                    # get the DayRate document from the database if it exists
        if day_information is None:                                             # if it doesn't exist
            day_information = formats.day_information                           # create an empty object
            day_information['day'] = day
        try:
            del day_information['_id']                                          # delete the id attribute of the document if it exists (to avoid duplicate ids)
        except KeyError:
            pass
        session['day_information'] = day_information                            # set the DayRating as a session variable
        return redirect('day_info')                                             # redirect to the rating page
    return render_template('pick_day.html', title="Pick a Day to Rate", form=form)


@app.route('/groups', methods=['POST', 'GET'])
def groups():
    """
    Redirects to and renders the groups page.
    """
    check_login()
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    my_groups = db.get_my_groups(username)                                      # get user's groups
    groups = []
    for group in my_groups:                                                     # iterate over groups
        groups.append((quote_plus(group['name']), group['name']))               # append tuple of URL encoded group name and string group name to list
    return render_template('groups.html', title="{}'s Groups".format(username), # render template
                           groups=groups)


@app.route('/create_group', methods=['POST', 'GET'])
def create_group():
    """

    """
    check_login()
    form = forms.CreateGroup()
    if form.validate_on_submit():
        try:
            username = session['username']                                              # define username variable
        except:
            return redirect('login')
        result, feedback, id = db.create_group(form.name.data, username, form.include_user.data)
        flash(feedback)
        return redirect("/groups")
    form.include_user.data = True
    return render_template('create_group.html', title="Create Group", form=form)


@app.route('/display_group', methods=['POST', 'GET'])
def display_group(): # this process needs validation/feedback
    check_login()
    group_name = request.args.get('group_name')
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    group_data = db.get_group_data(username, group_name)
    if len(group_data) < 1:
        return redirect('/groups')
    group_data = group_data[0]
    group_users = group_data['users']
    owner = False
    owner_username = group_data['owner']
    if owner_username == username:
        owner = True
    encoded = (quote_plus(group_name), quote_plus(owner_username))
    return render_template("group_display.html", title=group_name, group_users=group_users,
                           group_name=group_name, owner=owner, encoded=encoded)


@app.route('/group_dash', methods=['POST', 'GET'])
def group_dash():
    check_login()
    group_name = request.args.get('group_name')
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    group_data = db.get_group_data(username, group_name)[0]
    group_users = group_data['users']
    color_options = formats.get_group_color_options(group_users)
    start_date = group_data['create_date']
    owner = group_data['owner']
    group_preferences = db.get_group_preferences(group_name, owner)
    group_user_stats = stats.group_user_stats(group_users, group_preferences['group_num_ratings_stats'], start_date=start_date)
    summary_stats = stats.group_summary(group_users, group_preferences, start_date=start_date)
    group_stats = []
    for stat in group_user_stats:
        group_stats.append(stat)
    return render_template("group_dash.html", title="{} Dashboard".format(group_name),
                           group_user_stats=group_user_stats, group_name=group_name,
                           group_name_encoded=quote_plus(group_name),
                           summary_stats=summary_stats, group_stats=group_stats,
                           color_options=color_options, group_users=group_users)


@app.route('/group_dash_data', methods=['POST', 'GET'])
def group_dash_data():
    check_login()
    group_name = request.args.get('group_name')
    try:
        username = session['username']                                          # define username variable
    except:
        return redirect('login')
    days, ratings, labels = db.get_group_dash_data(username, group_name)
    #ratings_w_descriptions = add_descriptions(ratings, labels)
    #print(ratings_w_descriptions)
    #return { "x" : days, "y" : ratings_w_descriptions, "labels" : labels}
    return { "x" : days, "y" : ratings, "labels" : labels }


@app.route('/get_group_users', methods=['POST', 'GET'])
def get_group_users():
    check_login()
    try:
        username = session['username']                                          # define username variable
    except:
        return redirect('login')
    group_name = request.args.get('group_name')
    group_users = db.get_group_dash_data(session['username'], group_name, only_group_users=True)
    return { "group_users" : group_users }


@app.route('/add_user_to_group', methods=['POST', 'GET'])
def add_user_to_group():
    check_login()
    form = forms.AddUserToGroupForm()
    group_name = request.args.get('group_name')
    if form.validate_on_submit():
        username_to_add = form.username.data
        if len(db.find_user(username_to_add)) >= 1:
            try:
                username = session['username']                                              # define username variable
            except:
                return redirect('login')
            insert_result, feedback, _ = db.insert_user_to_group(username_to_add, group_name, username)
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
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    user_list = db.get_group_data(username, group_name)[0]['users']
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
        try:
            username = session['username']                                              # define username variable
        except:
            return redirect('login')
        if username == db.get_group_data(username, group_name)[0]['owner']:
            delete_result, feedback, _ = db.delete_group(username, group_name)
            flash(feedback)
            if delete_result:
                return redirect("/display_group?group_name={}".format(quote_plus(group_name)))
    return render_template('delete_group.html', form=delete_form, group_name=group_name)


@app.route('/user_preferences', methods=['POST', 'GET'])
def user_preferences():
    check_login()
    preferences_form = forms.UserPreferencesForm()
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    user_preferences_list = db.get_user_preferences(username)
    if preferences_form.validate_on_submit():
        result, feedback, _ = db.save_user_preferences(preferences_form, username)
        flash(feedback)
        if result:
            return redirect("/dash")
    if user_preferences is not None:
        preferences_form.num_ratings_display.data = int(user_preferences_list['num_ratings_display'])
        preferences_form.num_ratings_stats.data = int(user_preferences_list['num_ratings_stats'])
        preferences_form.stat_decimals.data = int(user_preferences_list['stat_decimals'])
    return render_template('user_preferences.html', form=preferences_form, username=username)


@app.route('/group_preferences', methods=['POST', 'GET'])
def group_preferences():
    check_login()
    group_name = request.args.get('group_name')
    preferences_form = forms.GroupPreferencesForm()
    try:
        username = session['username']                                              # define username variable
    except:
        return redirect('login')
    group_preferences_list = db.get_group_preferences(group_name, username)
    if preferences_form.validate_on_submit():
        result, feedback, _ = db.save_group_preferences(preferences_form, username, group_name)
        flash(feedback)
        if result:
            return redirect("/group_dash?group_name={}".format(quote_plus(group_name)))
    if group_preferences is not None:
        preferences_form.group_num_ratings_display.data = int(group_preferences_list['group_num_ratings_display'])
        preferences_form.group_num_ratings_stats.data = int(group_preferences_list['group_num_ratings_stats'])
        preferences_form.group_stat_decimals.data = int(group_preferences_list['group_stat_decimals'])
    return render_template('group_preferences.html', form=preferences_form, group_name=group_name)


@app.route('/set_cookie', methods=['POST', 'GET'])
def set_cookie():
    """
    Sets cookie in browser
    """
    name = request.args.get('name')
    value = request.args.get('value')
    if (name is None) or (value is None):
        return None
    response = make_response("Setting a cookie")
    response.set_cookie(name, value, max_age=60*60*24*365*2)
    return response


@app.route('/get_cookie_color', methods=['POST', 'GET'])
def get_cookie_color():
    """
    Returns color cookie
    """
    color = request.cookies.get('color')
    return {"color" : color}


def check_login():
    if 'username' in session:
        return
    else:
        return redirect("/login")

def add_descriptions(ratings, labels):
    ratings_w_descriptions = []
    for i, rating_series in enumerate(ratings):
        ratings_w_description = []
        for rating in rating_series:
            ratings_w_description.append({"meta" : labels[i], "value" : rating})
        ratings_w_descriptions.append(ratings_w_description)
    return ratings_w_descriptions

if __name__ == '__main__':
    app.run(debug=True)
