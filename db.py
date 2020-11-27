import pymongo
from bson.objectid import ObjectId
from datetime import date
import datetime
from urllib.parse import quote_plus
import formats
from config import ROOT_USER, ROOT_PWD, SERVER_PUBLIC_IP


"""
Bash command for transferring directory to server:
'sudo scp -r -i dayrate.pem dayrate ec2-user@ec2-18-221-31-5.us-east-2.compute.amazonaws.com:/home/ec2-user'
"""


connection_string = "mongodb://{}:{}@{}/admin".format(ROOT_USER, ROOT_PWD, SERVER_PUBLIC_IP)    # string for connecting to mongoDB
bad_result = False, "Something went wrong :/ Try again?", None                                  # generic error response


def get_client():
    """
    connects to the dayrate database
    """
    client = pymongo.MongoClient(connection_string)                             # use connection string to instantiate client object
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
    client = get_client()                                                       # construct client
    users_collection = client["users"]                                          # get 'users' collection
    query = {"username" : user, "password" : pword}                             # generate username and password query
    result = list(users_collection.find(query))                                 # return results of query in users collection
    if len(result) != 1:                                                        # if there are not one result, something was incorrect
        return False, "Username and password combination not found!", None      # return response
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
            return bad_result


def day_info(date, username):
    """
    returns a DayRate

    params:
        date: string date of DayRate
        username: string username

    returns:
        dictionatry of DayRate information
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

    params:
        day_information: dictionary of DayRate info
        username: string username

    returns:
        tuple of ( bool success, string feedback, string document_id or None)
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
            return bad_result
    else:
        update_result = days_collection.replace_one({ "username" : username, "day" : day_information["day"]},
                                                     day_information)
        if update_result.acknowledged:
            return True, "DayRate input successfully", None
        else:
            return bad_result


def get_dash_info(username):
    """
    Retrieves the user's dashboard information

    param:
        username: string username

    returns:
        list of tuples: (string day, string rating, string url encoded day)
    """
    client = get_client()
    days_collection = client["days"]
    past_n_days = get_past_n_days(username, 10)
    ratings = []
    for rating in past_n_days:
        ratings.append((rating['day'], rating['rating'], quote_plus(rating['day'])))
    return ratings


def get_past_n_days(username, n):
    """
    Returns the past n DayRates

    params:
        username: string username
        n: int number of ratings to retrieve

    returns:
        list of dictionaries containing DayRate information
    """
    client = get_client()
    days_collection = client["days"]
    query = {"username" : username}
    results = days_collection.find(query).sort([('timestamp', 1)]).limit(n)
    return unwrap_query_results(results)


def get_my_groups(username):
    """
    Returns the group information for a user

    param:
        username: string username

    returns:
        list of dictionaries containing group information
    """
    client = get_client()
    groups_collection = client["groups"]
    query = {"$or":[ {"users" : username },
                     {"created_by" : username},
                     {"users" : username},
                     {"owner" : username} ]}
    results = groups_collection.find(query)
    return unwrap_query_results(results)


def unwrap_query_results(query_results):
    """
    Converts query results into a list of dictionaries

    param:
        query result

    returns:
        list of dictionaries
    """
    result_list = []
    for result in query_results:
        result_list.append(result)
    return result_list


def create_group(group_name, username, include_user):
    """
    Create a group document

    params:
        group_name: name of new group
        username: string username
        include_user: bool include the user in the group

    returns:
        results of group creation
    """
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
        return bad_result


def get_today():
    """
    return today's date string
    """
    datetime = date.today()
    return str(datetime.year) + "-" + str(datetime.month) + "-" + str(datetime.day)


def get_group_data(username, group_name):
    """
    return the data of a group

    params:
        username: string username
        group_name: string name of group

    returns:
        dictionary containing specified group information
    """
    client = get_client()
    groups_collection = client["groups"]
    result = groups_collection.find({"$and": [ {"name" : group_name},
                                    {"$or": [ {"created_by" : username},
                                    {"users" : username},
                                    {"owner" : username}]}]})
    return unwrap_query_results(result)


def find_user(username):
    """
    return the information of specified user
    """
    client = get_client()
    users_collection = client["users"]
    user_results = users_collection.find({"username" : username})
    return unwrap_query_results(user_results)


def insert_user_to_group(username_to_add, group_name, username):
    """
    Add a user to a group

    params:
        username_to_add: string username to add to group
        group_name: string name of group
        username: string username of user performing operation

    returns:
        results of insert
    """
    client = get_client()
    groups_collection = client["groups"]
    group_data = get_group_data(username, group_name)
    if username_to_add in group_data[0]['users']:
        return False, "{} is already in {}".format(username_to_add, group_name), None
    insert_result = groups_collection.update({"name" : group_name, "owner" : username},
                                             {"$push" : {"users" : username_to_add}})
    if insert_result['updatedExisting']:
        return True, "{} added to {}".format(username_to_add, group_name), None
    else:
        return bad_result


def change_group_owner(current_owner, new_owner, group_name):
    """
    Change the owner of a group

    params:
        current_owner: string username of current user (and current owner)
        new_owner: string username of new owner
        group_name: string name of group

    returns:
        result of update
    """
    client = get_client()
    groups_collection = client["groups"]
    update_result = groups_collection.update_one({"name" : group_name, "owner" : current_owner},
                                             {"$set" : {"owner" : new_owner}})
    if update_result.acknowledged:
        return True, "{} is the new owner of {}".format(new_owner, group_name), None
    return bad_result


def delete_group(owner_name, group_name):
    """
    Delete a group

    params:
        owner_name: string username of group owner (current user)
        group_name: string name of group

    returns:
        results of update
    """
    client = get_client()
    groups_collection = client["groups"]
    delete_result = groups_collection.delete_one({"owner" : owner_name, "name" : group_name})
    if delete_result.acknowledged:
        return True, "{} was successfully deleted".format(group_name), None
    return bad_result


def get_group_dash_data(username, group_name):
    """
    Get the information for a group's dashboard. (This can totally be optimized at some later point)

    params:
        username: string username
        group_name: string name of group

    returns:
        tuple (list of sorted day strings, list of string ratings, list of string users in group)
    """
    group_users = get_group_data(username, group_name)[0]['users']
    data = {}
    user_datas = {}
    for username in group_users:
        user_data = get_dash_info(username)
        user_datas.update({username : user_data})
        for day_tuple in user_data:
            day = day_tuple[0]
            if day not in data.keys():
                data.update({day : {}})

    for day in data.keys():
        for username in user_datas.keys():
            user_data_dic = data[day]
            user_data_dic.update({username : None})
            for rating in user_datas[username]:
                if rating[0] == day:
                    user_data_dic[username] = rating[1]
    days = list(data.keys())
    days.sort(key = lambda date: datetime.datetime.strptime(date, formats.date))
    ratings = []
    for username in user_datas.keys():
        ratings_by_day = []
        for day in days:
            rating = data[day][username]
            ratings_by_day.append(rating)
        ratings.append(ratings_by_day)
    return days, ratings, list(user_datas.keys())
