"""
Contains formats for data structures like the day rate dictionary
"""
day_information = {"day" : "",
                   "rating": "",
                   "username": "",
                   "comments": ""}

date = "%Y-%m-%d"

dayrate_description = "DayRate is an app for tracking personal statistics on " +    \
                      "mood, energy, overall satisfaction, and more. " +    \
                      "Analyze your habits, check in on those you ca" +    \
                      "re about, and plan for a happier, more meaningful future."

def fill_day_info(form, day, username):
    day_information["day"] = day
    day_information["username"] = username
    day_information["rating"] = form.rating.data
    day_information["comments"] = form.comments.data
    return day_information
