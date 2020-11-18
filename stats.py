import db
import numpy as np

def last_n_ratings(username, n):
    last_n_entries = db.get_past_n_days(username, n)
    ratings = []
    for entry in last_n_entries:
        ratings.append(entry['rating'])
    return ratings

def last_n_average(username, n):
    return np.mean(last_n_ratings(username, n))

def last_n_std(username, n):
    return np.std(last_n_ratings(username, n))

def last_n_sum(username, n):
    return np.sum(last_n_ratings(username, n))

def stat_summary(username, n):
    return [{"stat_name" : "mean", "stat" : round(last_n_average(username, n), 3)},
            {"stat_name" : "std", "stat" : round(last_n_std(username, n), 3)},
            {"stat_name" : "sum", "stat" : round(last_n_sum(username, n), 3)}]
