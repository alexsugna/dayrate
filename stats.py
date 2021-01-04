import db
import numpy as np
import default_preferences as dp

def last_n_ratings(username, n, start_date=None):
    """
    return the last n ratings for the specified user
    """
    last_n_entries = db.get_past_n_days(username, n, start_date=start_date)
    ratings = []
    for entry in last_n_entries:
        ratings.append(entry['rating'])
    return ratings


def last_n_average(username, n, start_date=None): # calculates the mean of the last n ratings
    return np.mean(last_n_ratings(username, n, start_date=start_date))

def last_n_std(username, n, start_date=None):    # standard deviation of last n ratings
    return np.std(last_n_ratings(username, n, start_date=start_date))

def last_n_sum(username, n, start_date=None):    # sum of last n ratings
    return np.sum(last_n_ratings(username, n, start_date=start_date))


def stat_summary(username, n, precision, start_date=None):
    """
    returns a stat summary for the last n ratings of the specified user
    """
    n = int(n)
    precision = int(precision)
    return [{"stat_name" : "mean", "stat" : round(last_n_average(username, n, start_date=start_date), precision)},
            {"stat_name" : "std", "stat" : round(last_n_std(username, n, start_date=start_date), precision)},
            {"stat_name" : "sum", "stat" : round(last_n_sum(username, n, start_date=start_date), precision)}]


def group_user_stats(group_users, n, start_date=None):
    """
    returns a list of average stats for a group
    """
    group_stats = []
    for username in group_users:
        user_stats = [stat_summary(username, n, dp.group_stat_decimals, start_date=start_date)]
        user_stats.insert(0, username)
        group_stats.append(user_stats)
    return group_stats


def group_summary(group_users, group_preferences, start_date=None):
    """
    returns a summary for the specified group
    """
    all_ratings = []
    decimals = group_preferences['group_stat_decimals']
    for username in group_users:
        all_ratings += last_n_ratings(username, group_preferences["group_num_ratings_stats"], start_date=start_date)
    return [{"stat_name" : "mean", "stat" : round(np.mean(all_ratings), decimals)},
            {"stat_name" : "std", "stat" : round(np.std(all_ratings), decimals)},
            {"stat_name" : "sum", "stat" : round(np.sum(all_ratings), decimals)}]
