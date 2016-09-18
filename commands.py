from config import API_URL
import requests


def welcome(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def get_info(update):
    user = update.message.from_user
    user_name = user.first_name + ' ' + user.last_name
    group = update.message.chat_id
    user_id = user.id
    return user_name.strip(), user_id, group


def info(bot, update):
    user_name, user_id, group = get_info(update)
    bot.sendMessage(group, text=user_name + ' ' + user_id)


# Register group (should automate this though)
def register_group(bot, update):
    user_name, user_id, group = get_info(update)

    # Server request
    data = {
        'group': group
    }
    r = requests.post(API_URL + 'register_group', json=data)

    # Response handling
    if r.status_code == 200:
        bot.sendMessage(group, text='Group registered')
    else:
        bot.sendMessage(group, text='Group already registered / registration failed')


# Registration command
def register(bot, update):
    user_name, user_id, group = get_info(update)

    # Server request
    data = {
        'id': user_id,
        'username': user_name,
        'groupID': group
    }
    r = requests.post(API_URL + 'register', json=data)

    # Response handling
    if r.status_code == 200:
        bot.sendMessage(group, text=user_name + ': Successful registration')
    else:
        bot.sendMessage(group, text=user_name + ': Registration failed / already registered')


# Start meal
def start_meal(bot, update, args):
    user_name, user_id, group = get_info(update)

    # TODO: Check the number of args
    meal_type = args[0].strip()

    # Request
    data = {
        'group': group,
        'meal_type': meal_type
    }
    r = requests.post(API_URL + 'add_meal', json=data)

    # Response handling
    if r.status_code == 200:
        bot.sendMessage(group, text='Who is eating ' + meal_type + '?')
    else:
        bot.sendMessage(group, text='Another meal is running / unable to start meal')


# End meal
def end_meal(bot, update, args):
    user_name, user_id, group = get_info(update)

    # Request
    data = {
        'group': group
    }
    r = requests.post(API_URL + 'end_meal', json=data)

    # Response handling
    # Do not end the meal immediately, should trigger some handlers for warnings
    # E.g. 15min / 10min
    if r.status_code == 200:
        bot.sendMessage(group, text='Meal ended')
    else:
        bot.sendMessage(group, text='Unable to end meal')


def meal_participation(bot, update, args, cooked):
    user_name, user_id, group = get_info(update)

    # Argument handling
    portion = 1
    if len(args) > 0:
        # TODO: Check arg value
        portion = int(args[0])
    portion_text = str(portion) + (' portion' if portion == 1 else ' portions')

    # Request
    data = {
        'user_id': user_id,
        'group': group,
        'portions': portion,
        'cooked': cooked
    }
    r = requests.post(API_URL + 'eating', json=data)

    if r.status_code == 200:
        if portion == 0:
            bot.sendMessage(group, text=user_name + ' removed from meal')
        elif cooked:
            bot.sendMessage(group, text='Thanks for cooking, ' + user_name + '! You are eating ' + portion_text)
        else:
            bot.sendMessage(group, text=user_name + ' eating ' + portion_text)
    else:
        bot.sendMessage(group, text='Unable to update, is a meal started?')


# Eating
def eating(bot, update, args):
    meal_participation(bot, update, args, cooked=False)


# Cooking
def cooking(bot, update, args):
    meal_participation(bot, update, args, cooked=True)


def meal_info(bot, update, args):
    user_name, user_id, group = get_info(update)

    # Request
    data = {
        'group': group
    }
    r = requests.post(API_URL + 'meal_info', json=data)

    if r.status_code == 200:
        meal_participations = r.json()
        output = ''
        total_portions = 0
        if len(meal_participations) == 0:
            bot.sendMessage(group, 'No information to display')

        for mp in meal_participations:
            output += str(mp['user_name']) + ' '
            output += str(mp['portions']) + (' portion' if mp['portions'] == 1 else ' portions')
            output += ' - cooking' if mp['cooked'] else ''
            output += '\n'
            total_portions += mp['portions']
        output += str(total_portions) + (' portion' if total_portions == 1 else ' portions') + ' required'
        bot.sendMessage(group, text=output)
    else:
        bot.sendMessage(group, text='Unable to retrieve meal information')
