'''
Contains formats for data structures like the day rate dictionary
'''
day_information = {'day' : '',
                   'rating': '',
                   'username': '',
                   'comments': ''}

date = '%Y-%m-%d'

dayrate_description = 'DayRate is an app for tracking personal statistics on ' +    \
                      'mood, energy, overall satisfaction, and more. ' +    \
                      'Analyze your habits, check in on those you ca' +    \
                      're about, and plan for a happier, more meaningful future.'

color_options = "<option value='red' id='red'>Red</option> \
                <option value='blue' id='blue'>Blue</option> \
                <option value='green' id='green'>Green</option> \
                <option value='orange' id='orange'>Orange</option> \
                <option value='indigo' id='indigo'>Indigo</option> \
                <option value='purple' id='purple'>Purple</option> \
                <option value='pink' id='pink'>Pink</option> \
                <option value='yellow' id='yellow'>Yellow</option> \
                <option value='teal' id='teal'>Teal</option> \
                <option value='cyan' id='cyan'>Cyan</option> \
                <option value='white' id='white'>White</option> \
                <option value='gray' id='gray'>Gray</option>"


def fill_day_info(form, day, username):
    day_information['day'] = day
    day_information['username'] = username
    day_information['rating'] = form.rating.data
    day_information['comments'] = form.comments.data
    return day_information


def get_group_color_options(group_members):
    html = ""
    for member in group_members:
        html += "<div><label for='color-select-{}'>{}'s color  </label>".format(member, member)
        html += "<select name='color-select-{}' id='color-select-{}' onchange='changeColors({})'>".format(member, member, member)
        html += color_options
        html += "</select></div>"
    return html
