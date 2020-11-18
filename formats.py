"""
Contains formats for data structures like the day rate dictionary
"""
day_information = {"day" : "",
                   "rating": "",
                   "username": "",
                   "comments": ""}

def fill_day_info(form, day, username):
    day_information["day"] = day
    day_information["username"] = username
    day_information["rating"] = form.rating.data
    day_information["comments"] = form.comments.data
    return day_information
