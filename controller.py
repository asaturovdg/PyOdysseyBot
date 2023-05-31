import telebot
import dao
from telebot import types

pending_team_invitation_requests = {}
pending_team_deletion_requests = {}
pending_project_creation_requests = {}
pending_project_deletion_requests = {}
pending_task_creation_requests = {}
pending_task_deletion_requests = {}

callback_view_info = {}

status_localize = {'planned': 'Запланированно',
                   'active': 'В процессе',
                   'done': 'Выполнено'}

bot = telebot.TeleBot('------')


@bot.message_handler(commands=['start'])
def start(message):
    dao.create_user(message.from_user.id, message.from_user.first_name)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = [['Список команд', 'Создать команду'], ['Пригласить в команду', 'Удалить команду'],
               ['Создать проект', 'Удалить проект'], ['Создать задачу', 'Удалить задачу']]

    for titles in buttons:
        markup.add(types.KeyboardButton(titles[0]), types.KeyboardButton(titles[1]))

    bot.send_message(message.chat.id, 'Добро пожаловать', reply_markup=markup)


@bot.message_handler(commands=['teams'])
def teams(message):
    if not dao.get_user(message.from_user.id) is None:
        callback_view_info[message.from_user.id] = {}
        markup = types.InlineKeyboardMarkup()

        reply = "Список команд\n\n"

        teams_list = dao.get_teams_list(message.from_user.id)
        for index, team in enumerate(teams_list):
            team_msg = f"{index + 1}. {team}"
            reply += team_msg + '\n'
            markup.add(types.InlineKeyboardButton(team, callback_data='t_v_' + team))

        bot.send_message(message.chat.id, reply, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if not dao.get_user(message.from_user.id) is None:
        match message.text.lower():
            case "список команд":
                teams(message)
            case "создать команду":
                bot.send_message(message.chat.id,
                                 'Введите название команды \n(Без специальных знаков и не более 30 символов):')
                bot.register_next_step_handler(message, create_team)
            case "пригласить в команду":
                reply = "В какую команду пригласить пользователя? (Введите цифру перед названием команды)\n\n (Приглашать можно только в команды, созданные вами)\n\n"

                teams_list = dao.get_teams_list_where_creator(message.from_user.id)
                for index, team in enumerate(teams_list):
                    team_msg = f"{index + 1}. {team}"
                    reply += team_msg + '\n'

                bot.send_message(message.chat.id, reply)
                bot.register_next_step_handler(message, get_who_to_invite)
            case "удалить команду":
                reply = "Какую команду удалить? (Введите цифру перед названием команды)\n\n (Удалить можно только команды, созданные вами)\n\n"

                teams_list = dao.get_teams_list_where_creator(message.from_user.id)
                for index, team in enumerate(teams_list):
                    team_msg = f"{index + 1}. {team}"
                    reply += team_msg + '\n'

                bot.send_message(message.chat.id, reply)
                bot.register_next_step_handler(message, confirm_team_delete)
            case "создать проект":
                reply = "Для какой команды создать проект? (Введите цифру перед названием команды)\n\n"

                teams_list = dao.get_teams_list(message.from_user.id)
                for index, team in enumerate(teams_list):
                    team_msg = f"{index + 1}. {team}"
                    reply += team_msg + '\n'

                bot.send_message(message.chat.id, reply)
                bot.register_next_step_handler(message, get_project_name)
            case "удалить проект":
                reply = "Из какой команды удалить проект? (Введите цифру перед названием команды)\n\n (Удалить можно только проекты из команд, созданных вами)\n\n"

                teams_list = dao.get_teams_list_where_creator(message.from_user.id)
                for index, team in enumerate(teams_list):
                    team_msg = f"{index + 1}. {team}"
                    reply += team_msg + '\n'

                bot.send_message(message.chat.id, reply)
                bot.register_next_step_handler(message, which_project_to_delete)
            case "создать задачу":
                reply = "Для какой команды создать задачу? (Введите цифру перед названием команды)\n\n"

                teams_list = dao.get_teams_list(message.from_user.id)
                for index, team in enumerate(teams_list):
                    team_msg = f"{index + 1}. {team}"
                    reply += team_msg + '\n'

                bot.send_message(message.chat.id, reply)
                bot.register_next_step_handler(message, get_project_where_to_create_task)
            case "удалить задачу":
                reply = "Из какой команды удалить задачу? (Введите цифру перед названием команды)\n\n (Удалить можно только задачи из команд, созданных вами)\n\n"

                teams_list = dao.get_teams_list_where_creator(message.from_user.id)
                for index, team in enumerate(teams_list):
                    team_msg = f"{index + 1}. {team}"
                    reply += team_msg + '\n'

                bot.send_message(message.chat.id, reply)
                bot.register_next_step_handler(message, from_which_project_delete_task)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if not dao.get_user(call.from_user.id) is None:
        if "t_v_" in call.data:
            cb_team_view(call)
        elif "pr_v_" in call.data:
            cb_project_view(call)
        elif "ts_v_" in call.data:
            cb_task_view(call)
        elif "ch_s_" in call.data:
            cb_change_status(call)
        elif "acc_inv_" in call.data:
            accept_invitation(call)


def cb_team_view(call):
    team = call.data.replace('t_v_', '')

    callback_view_info[call.from_user.id]['team'] = team

    markup = types.InlineKeyboardMarkup()

    reply = f"Список участников команды\n<b>{team}</b>\n\n"

    members_list = dao.get_team_members(team)
    for index, member in enumerate(members_list):
        mention = f'<a href="tg://user?id={member["id"]}">{member["name"]}</a>'
        member_msg = f"{index + 1}. {mention}"
        reply += member_msg + "\n"

    reply += "\n\n"

    projects_list = dao.get_projects(team)
    for index, project in enumerate(projects_list):
        project_msg = f"{index + 1}. {project}"
        reply += project_msg + "\n"
        markup.add(types.InlineKeyboardButton(project, callback_data='pr_v_' + project))

    bot.send_message(call.from_user.id, reply, parse_mode='html', reply_markup=markup)


def cb_project_view(call):
    project = call.data.replace('pr_v_', '')
    team = callback_view_info[call.from_user.id]['team']

    callback_view_info[call.from_user.id]['project'] = project
    markup = types.InlineKeyboardMarkup()

    reply = f"Проект\n<b>{project}</b>\n\n"
    tasks_list = dao.get_tasks(project, team)
    for index, task in enumerate(tasks_list):
        task_msg = f"{index + 1}. {task}"
        reply += task_msg + "\n"
        markup.add(types.InlineKeyboardButton(index + 1, callback_data='ts_v_' + task))
    bot.send_message(call.from_user.id, reply, parse_mode='html', reply_markup=markup)


def cb_task_view(call):
    task = call.data.replace('ts_v_', '')
    team = callback_view_info[call.from_user.id]['team']
    project = callback_view_info[call.from_user.id]['project']

    task_status = status_localize[dao.get_task_status(project, team, task)]

    callback_view_info[call.from_user.id]['task'] = task
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(status_localize['planned'], callback_data='ch_s_planned'),
               types.InlineKeyboardButton(status_localize['active'], callback_data='ch_s_active'),
               types.InlineKeyboardButton(status_localize['done'], callback_data='ch_s_done'))

    reply = f"Задача\n<b>{task}</b>\n\nСтатус: {task_status}\n\nКнопками ниже можно изменить статус задачи"
    bot.send_message(call.from_user.id, reply, parse_mode='html', reply_markup=markup)


def cb_change_status(call):
    status = call.data.replace('ch_s_', '')

    team = callback_view_info[call.from_user.id]['team']
    project = callback_view_info[call.from_user.id]['project']
    task = callback_view_info[call.from_user.id]['task']

    dao.change_task_status(project, team, task, status)
    bot.send_message(call.from_user.id,
                     f"Статус задачи <b>{task}</b> изменен на <b><u>{status_localize[status]}</u></b>",
                     parse_mode='html')


def accept_invitation(call):
    user_and_who_invited = call.data.replace('acc_inv_', '').split('_')
    user = int(user_and_who_invited[0])
    who_invited = int(user_and_who_invited[1])
    team = pending_team_invitation_requests[(user, who_invited)]
    dao.insert_in_team(user, team)
    pending_team_invitation_requests.pop((user, who_invited))
    bot.send_message(user, f'Успешно! Вы стали участником команды <b>{team}</b>', parse_mode='html')
    user_name = dao.get_user(user)['name']
    mention = f'<a href="tg://user?id={user}">{user_name}</a>'

    bot.send_message(who_invited, f"{mention} принял приглашение в команду <b>{team}</b>!", parse_mode='html')


def create_team(message):
    name = message.text
    if "_" not in name and len(name) <= 30:
        if dao.get_team(name) is None:
            dao.create_team(message.from_user.id, name)
            bot.send_message(message.chat.id, f"Успешно создана команда: <b>{name}</b>", parse_mode='html')
        else:
            bot.send_message(message.chat.id, "Команда с таким названием уже существует")
    else:
        bot.send_message(message.chat.id, "Недопустимое название команды")


def get_who_to_invite(message):
    teams_list = dao.get_teams_list_where_creator(message.from_user.id)
    try:
        if int(message.text) in range(1, len(teams_list) + 1):
            pending_team_invitation_requests[message.from_user.id] = teams_list[int(message.text) - 1]
            bot.send_message(message.chat.id,
                             'Перешлите сообщение от пользователя, которого хотите пригласить в команду')
            bot.register_next_step_handler(message, send_invitation)
        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор команды')
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор команды')


def send_invitation(message):
    user_id = message.forward_from.id
    if not dao.get_user(user_id) is None:
        team = pending_team_invitation_requests[message.from_user.id]
        members = dao.get_team_members(team)
        members_ids = []
        for member in members:
            members_ids.append(member['id'])
        if not user_id in members_ids:
            pending_team_invitation_requests[(user_id, message.from_user.id)] = pending_team_invitation_requests[
                message.from_user.id]
            pending_team_invitation_requests.pop(message.from_user.id)

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Принять приглашение',
                                                  callback_data='acc_inv_' + str(user_id) + '_' + str(
                                                      message.from_user.id)))

            bot.send_message(message.from_user.id, 'Приглашение отправлено')

            bot.send_message(user_id,
                             f'<b>{message.from_user.first_name}</b> приглашает вас присоедениться к команде <b>{pending_team_invitation_requests[(user_id, message.from_user.id)]}</b>',
                             parse_mode='html', reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, 'Данный пользователь уже является участником этой команды')
    else:
        bot.send_message(message.from_user.id, 'Данный пользователь не зарегистрирован')


def confirm_team_delete(message):
    teams_list = dao.get_teams_list_where_creator(message.from_user.id)
    try:
        if int(message.text) in range(1, len(teams_list) + 1):
            team = teams_list[int(message.text) - 1]
            pending_team_deletion_requests[message.from_user.id] = team
            bot.send_message(message.chat.id,
                             f'Вы уверены, что хотите удалить команду <b>{team}</b>?\n\nДля подтверждения отправьте название команды (Выделено жирным)',
                             parse_mode='html')
            bot.register_next_step_handler(message, delete_team)
        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор команды')
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор команды')


def delete_team(message):
    if message.text in pending_team_deletion_requests.values():
        dao.delete_team(message.text)
        bot.send_message(message.chat.id, f'Успешно! Вы удалили команду <b>{message.text}</b>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Отмена процесса удаления команды')
    pending_team_deletion_requests.pop(message.from_user.id)


def get_project_name(message):
    teams_list = dao.get_teams_list(message.from_user.id)
    try:
        if int(message.text) in range(1, len(teams_list) + 1):
            pending_project_creation_requests[message.from_user.id] = teams_list[int(message.text) - 1]
            bot.send_message(message.chat.id,
                             'Введите название проекта (Без специальных знаков и не более 30 символов):')
            bot.register_next_step_handler(message, create_project)
        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор команды')
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор команды')


def create_project(message):
    if "_" not in message.text and len(message.text) <= 30:
        dao.create_project(message.text, pending_project_creation_requests[message.from_user.id])
        bot.send_message(message.chat.id, f"Успешно создан проект: <b>{message.text}</b>", parse_mode='html')
    else:
        bot.send_message(message.chat.id, "Недопустимое название проекта")
    pending_project_creation_requests.pop(message.from_user.id)


def which_project_to_delete(message):
    teams_list = dao.get_teams_list_where_creator(message.from_user.id)
    try:
        if int(message.text) in range(1, len(teams_list) + 1):
            team = teams_list[int(message.text) - 1]
            pending_project_deletion_requests[message.from_user.id] = team

            reply = "Какой проект удалить? (Введите цифру перед названием проекта)\n\n"

            projects_list = dao.get_projects(team)
            for index, project in enumerate(projects_list):
                project_msg = f"{index + 1}. {project}"
                reply += project_msg + '\n'

            bot.send_message(message.chat.id, reply)
            bot.register_next_step_handler(message, confirm_project_delete)

        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор команды')
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор команды')


def confirm_project_delete(message):
    team = pending_project_deletion_requests[message.from_user.id]
    projects_list = dao.get_projects(team)
    try:
        if int(message.text) in range(1, len(projects_list) + 1):
            project = projects_list[int(message.text) - 1]
            pending_project_deletion_requests[message.from_user.id] = [team, project]
            bot.send_message(message.chat.id,
                             f'Вы уверены, что хотите удалить проект <b>{project}</b>?\n\nДля подтверждения отправьте название проекта (Выделено жирным)',
                             parse_mode='html')
            bot.register_next_step_handler(message, delete_project)
        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор проекта')
            pending_project_deletion_requests.pop(message.from_user.id)
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор проекта')
        pending_project_deletion_requests.pop(message.from_user.id)


def delete_project(message):
    info = pending_project_deletion_requests[message.from_user.id]
    if message.text in info:
        team = info[0]
        project = info[1]
        dao.delete_project(team, project)
        bot.send_message(message.chat.id, f'Успешно! Вы удалили проект <b>{message.text}</b>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Отмена процесса удаления проекта')
    pending_project_deletion_requests.pop(message.from_user.id)


def get_project_where_to_create_task(message):
    teams_list = dao.get_teams_list(message.from_user.id)
    try:
        if int(message.text) in range(1, len(teams_list) + 1):
            team = teams_list[int(message.text) - 1]
            pending_task_creation_requests[message.from_user.id] = team

            reply = "Для какого проекта создать задачу? (Введите цифру перед названием проекта)\n\n"

            projects_list = dao.get_projects(team)
            for index, project in enumerate(projects_list):
                project_msg = f"{index + 1}. {project}"
                reply += project_msg + '\n'

            bot.send_message(message.chat.id, reply)
            bot.register_next_step_handler(message, get_task_name)
        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор команды')
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор команды')


def get_task_name(message):
    team = pending_task_creation_requests[message.from_user.id]
    projects_list = dao.get_projects(team)
    try:
        if int(message.text) in range(1, len(projects_list) + 1):
            project = projects_list[int(message.text) - 1]
            pending_task_creation_requests[message.from_user.id] = [team, project]
            bot.send_message(message.chat.id,
                             'Введите название задачи (Без специальных знаков и не более 30 символов):')
            bot.register_next_step_handler(message, create_task)
        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор проекта')
            pending_task_creation_requests.pop(message.from_user.id)
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор проекта')
        pending_task_creation_requests.pop(message.from_user.id)


def create_task(message):
    if "_" not in message.text and len(message.text) <= 30:
        info = pending_task_creation_requests[message.from_user.id]
        team = info[0]
        project = info[1]
        dao.create_task(team, project, message.text)
        bot.send_message(message.chat.id, f"Успешно создана задача: <b>{message.text}</b>", parse_mode='html')
    else:
        bot.send_message(message.chat.id, "Недопустимое название задачи")
    pending_task_creation_requests.pop(message.from_user.id)


def from_which_project_delete_task(message):
    teams_list = dao.get_teams_list_where_creator(message.from_user.id)
    try:
        if int(message.text) in range(1, len(teams_list) + 1):
            team = teams_list[int(message.text) - 1]
            pending_task_deletion_requests[message.from_user.id] = team

            reply = "Из какого проекта удалить задачу? (Введите цифру перед названием проекта)\n\n"

            projects_list = dao.get_projects(team)
            for index, project in enumerate(projects_list):
                project_msg = f"{index + 1}. {project}"
                reply += project_msg + '\n'

            bot.send_message(message.chat.id, reply)
            bot.register_next_step_handler(message, which_task_to_delete)

        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор команды')
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор команды')


def which_task_to_delete(message):
    team = pending_task_deletion_requests[message.from_user.id]
    projects_list = dao.get_projects(team)
    try:
        if int(message.text) in range(1, len(projects_list) + 1):
            project = projects_list[int(message.text) - 1]
            pending_task_deletion_requests[message.from_user.id] = [team, project]

            reply = "Какую задачу удалить? (Введите цифру перед названием задачи)\n\n"

            tasks_list = dao.get_tasks(project, team)
            for index, task in enumerate(tasks_list):
                task_msg = f"{index + 1}. {task}"
                reply += task_msg + '\n'

            bot.send_message(message.chat.id, reply)
            bot.register_next_step_handler(message, confirm_task_delete)

        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор проекта')
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор проекта')


def confirm_task_delete(message):
    info = pending_task_deletion_requests[message.from_user.id]
    team = info[0]
    project = info[1]
    tasks_list = dao.get_tasks(project, team)
    try:
        if int(message.text) in range(1, len(tasks_list) + 1):
            task = tasks_list[int(message.text) - 1]
            pending_task_deletion_requests[message.from_user.id] = [team, project, task]
            bot.send_message(message.chat.id,
                             f'Вы уверены, что хотите удалить задачу <b>{task}</b>?\n\nДля подтверждения отправьте название задачи (Выделено жирным)',
                             parse_mode='html')
            bot.register_next_step_handler(message, delete_task)
        else:
            bot.send_message(message.chat.id, 'Недопустимый выбор задачи')
            pending_task_deletion_requests.pop(message.from_user.id)
    except ValueError:
        bot.send_message(message.chat.id, 'Недопустимый выбор задачи')
        pending_task_deletion_requests.pop(message.from_user.id)


def delete_task(message):
    info = pending_task_deletion_requests[message.from_user.id]
    if message.text in info:
        team = info[0]
        project = info[1]
        dao.delete_task(team, project, message.text)
        bot.send_message(message.chat.id, f'Успешно! Вы удалили задачу <b>{message.text}</b>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Отмена процесса удаления задачи')
    pending_task_deletion_requests.pop(message.from_user.id)
