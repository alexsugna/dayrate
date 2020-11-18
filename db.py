import pymongo
from bson.objectid import ObjectId
from datetime import date
from urllib.parse import quote_plus

ROOT_USER = "admin"
ROOT_PWD = "password"
SERVER_PUBLIC_IP = "3.21.227.42"

connection_string = "mongodb://{}:{}@{}/admin".format(ROOT_USER, ROOT_PWD, SERVER_PUBLIC_IP)

def get_client():
    """
    connects to the dayrate database
    """
    client = pymongo.MongoClient(connection_string)
    return client.dayrate


def validate_login(user, pword):
    """
    Checks for username and password in users collection of database. If found,
    returns the _id parameter of the user.

    params:
        user: string username
        pword: string password

    returns:
        bool success
        string feedback to be displayed
        string _id of logged in user
    """
    client = get_client()
    users_collection = client["users"]
    query = {"username" : user, "password" : pword}
    result = list(users_collection.find(query))
    if len(result) != 1:
        return False, "Username and password combination not found!", None
    else:
        return True, "Hello {}!".format(result[0]['username']), result[0]['_id']


def validate_account_creation(user, password, reenter_password):
    """
    Validates the input of new user with database, creates new user if successful.

    params:
        user: string username
        password: string users password
        reenter_password: string re enter user password to ensure it is correct

    returns:
        bool success
        string feedback to be displayed
        string _id of logged in user
    """
    client = get_client()
    users_collection = client["users"]
    if password != reenter_password:
        return False, "Password does not match Re-enter password.", None
    username_query = {"username" : user}
    username_result = list(users_collection.find(username_query))
    if len(username_result) != 0:
        return False, "Username taken!", None
    else:
        result = users_collection.insert_one({"username" : user, "password" : password})
        if result.acknowledged:
            return True, "Account created successfully!", result.inserted_id
        else:
            return False, "Something went wrong :/ Try again?", None

def day_info(date, username):
    """
    returns a dictionary of day information
    """
    client = get_client()
    days_collection = client["days"]
    query = {"day" : date, "username" : username}
    day_result = list(days_collection.find(query))
    if len(day_result) < 1:
        return None
    else:
        return day_result[0]

def save_dayrate(day_information, username):
    """
    Saves a DayRate
    """
    client = get_client()
    days_collection = client["days"]
    day_result = day_info(day_information['day'], username)
    if day_result is None:
        # no existing entry, input new item
        result = days_collection.insert_one(day_information)
        if result.acknowledged:
            return True, "DayRate input successfully", result.inserted_id
        else:
            return False, "Something went wrong :/ Try again?", None
    else:
        rating_id = day_result['_id']
        update_result = days_collection.replace_one({ "username" : username, "day" : day_information["day"]},
                                                     day_information)
        if update_result.acknowledged:
            return True, "DayRate input successfully", None
        else:
            return False, "Something went wrong :/ Try again?", None

def get_dash_info(username):
    client = get_client()
    days_collection = client["days"]
    past_n_days = get_past_n_days(username, 10)
    ratings = []
    for rating in past_n_days:
        ratings.append((rating['day'], rating['rating'], quote_plus(rating['day'])))
    return ratings

def get_past_n_days(username, n):
    client = get_client()
    days_collection = client["days"]
    query = {"username" : username}
    results = days_collection.find(query).sort([('timestamp', 1)]).limit(n)
    return unwrap_query_results(results)

def get_my_groups(username):
    client = get_client()
    groups_collection = client["groups"]
    query = {"$or":[ {"users" : username },
                     {"created_by" : username},
                     {"users" : username},
                     {"owner" : username} ]}
    results = groups_collection.find(query)
    return unwrap_query_results(results)

def unwrap_query_results(query_results):
    result_list = []
    for result in query_results:
        result_list.append(result)
    return result_list

def create_group(group_name, username, include_user):
    client = get_client()
    groups_collection = client["groups"]
    group_entry = {"name" : group_name, "created_by" : username,
                   "users" : [], "create_date" : get_today(),
                   "owner" : username}
    if include_user:
        group_entry["users"].append(username)
    result = groups_collection.insert_one(group_entry)
    if result.acknowledged:
        return True, "{} created successfully!".format(group_name), result.inserted_id
    else:
        return False, "Something went wrong :/ Try again?", None

def get_today():
    datetime = date.today()
    return str(datetime.year) + "-" + str(datetime.month) + "-" + str(datetime.day)

def get_group_data(username, group_name):
    client = get_client()
    groups_collection = client["groups"]
    result = groups_collection.find({"$and": [ {"name" : group_name},
                                    {"$or": [ {"created_by" : username},
                                    {"users" : username},
                                    {"owner" : username}]}]})
    return unwrap_query_results(result)
