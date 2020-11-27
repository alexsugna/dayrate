import db
import numpy as np


def last_n_ratings(username, n):
    """
    return the last n ratings for the specified user
    """
    last_n_entries = db.get_past_n_days(username, n)
    ratings = []
    for entry in last_n_entries:
        ratings.append(entry['rating'])
    return ratings


def last_n_average(username, n): # calculates the mean of the last n ratings
    return np.mean(last_n_ratings(username, n))

def last_n_std(username, n):    # standard deviation of last n ratings
    return np.std(last_n_ratings(username, n))

def last_n_sum(username, n):    # sum of last n ratings
    return np.sum(last_n_ratings(username, n))


def stat_summary(username, n):
    """
    returns a stat summary for the last n ratings of the specified user
    """
    return [{"stat_name" : "mean", "stat" : round(last_n_average(username, n), 3)},
            {"stat_name" : "std", "stat" : round(last_n_std(username, n), 3)},
            {"stat_name" : "sum", "stat" : round(last_n_sum(username, n), 3)}]


def group_user_stats(group_users, n):
    """
    returns a list of average stats for a group
    """
    group_stats = []
    for username in group_users:
        user_stats = [stat_summary(username, n)]
        user_stats.insert(0, username)
        group_stats.append(user_stats)
    return group_stats


def group_summary(group_users, n):
    """
    returns a summary for the specified group
    """
    all_ratings = []
    for username in group_users:
        all_ratings += last_n_ratings(username, n)
    return [{"stat_name" : "mean", "stat" : round(np.mean(all_ratings), 3)},
            {"stat_name" : "std", "stat" : round(np.std(all_ratings), 3)},
            {"stat_name" : "sum", "stat" : round(np.sum(all_ratings), 3)}]
