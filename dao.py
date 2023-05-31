from contextlib import closing
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import sql


def get_teams_list(id):
    teams = []

    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL("select {column} from {table} where {field} = %s::bigint order by {column} asc") \
                .format(column=sql.Identifier('team'),
                        table=sql.Identifier('user_to_team'),
                        field=sql.Identifier('user_id'))
            cursor.execute(select, (id,))
            for row in cursor:
                teams.append(row['team'])
    return teams


def get_teams_list_where_creator(id):
    teams = []

    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL("select {column} from {table} where {field} = %s::bigint order by {column} asc") \
                .format(column=sql.Identifier('name'),
                        table=sql.Identifier('team'),
                        field=sql.Identifier('creator'))
            cursor.execute(select, (id,))
            for row in cursor:
                teams.append(row['name'])
    return teams


def get_user(id):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL("select {fields} from {table} where {column} = %s") \
                .format(column=sql.Identifier('id'),
                        table=sql.Identifier('user'),
                        fields=sql.SQL(',').join([
                            sql.Identifier('id'),
                            sql.Identifier('name')
                        ]))
            cursor.execute(select, (id,))
            return cursor.fetchone()


def create_user(id, name):
    if get_user(id) is None:
        with closing(
                psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                insert = sql.SQL("insert into {} values (%s, %s)") \
                    .format(sql.Identifier('user'))
                cursor.execute(insert, (id, name))
            conn.commit()


def get_team(name):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL("select {column} from {table} where {column} = %s") \
                .format(column=sql.Identifier('name'),
                        table=sql.Identifier('team'))
            cursor.execute(select, (name,))
            return cursor.fetchone()


def insert_in_team(id, team):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            insert_user_to_team = sql.SQL("insert into {table}({fields}) values (%s, %s)") \
                .format(table=sql.Identifier('user_to_team'),
                        fields=sql.SQL(',').join([
                            sql.Identifier('user_id'),
                            sql.Identifier('team')
                        ]))
            cursor.execute(insert_user_to_team, (id, team))
            conn.commit()
    print(f"Добавлен пользователь: {id}, Команда: {team}")


def create_team(user_id, name):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            insert_team = sql.SQL("insert into {} values (%s, %s)") \
                .format(sql.Identifier('team'))
            cursor.execute(insert_team, (name, user_id))

            insert_user_to_team = sql.SQL("insert into {table}({fields}) values (%s, %s)") \
                .format(table=sql.Identifier('user_to_team'),
                        fields=sql.SQL(',').join([
                            sql.Identifier('user_id'),
                            sql.Identifier('team')
                        ]))
            cursor.execute(insert_user_to_team, (user_id, name))
            conn.commit()
    print(f"Создана команда: {name}, Создатель: {user_id}")


def delete_team(name):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            delete_team = sql.SQL("delete from {table} where {field} = %s") \
                .format(table=sql.Identifier('team'),
                        field=sql.Identifier('name'))
            cursor.execute(delete_team, (name,))
            conn.commit()
    print(f"Удалена команда: {name}")


def create_project(name, team):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            insert_project = sql.SQL("insert into {table}({fields}) values (%s, %s)") \
                .format(table=sql.Identifier('project'),
                        fields=sql.SQL(',').join([
                            sql.Identifier('name'),
                            sql.Identifier('team')
                        ]))
            cursor.execute(insert_project, (name, team))
            conn.commit()
    print(f"Создан проект: {name}, Команда: {team}")


def get_projects(team):
    projects = []

    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL("select {column} from {table} where {field} = %s order by {column} asc") \
                .format(column=sql.Identifier('name'),
                        table=sql.Identifier('project'),
                        field=sql.Identifier('team'))
            cursor.execute(select, (team,))
            for row in cursor:
                projects.append(row['name'])
    return projects


def delete_project(team, project):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            delete_project = sql.SQL("delete from {table} where {field1} = %s and {field2} = %s") \
                .format(table=sql.Identifier('project'),
                        field1=sql.Identifier('team'),
                        field2=sql.Identifier('name'))
            cursor.execute(delete_project, (team, project))
            conn.commit()
    print(f"Удален проект: {project}")


def create_task(team, project, task):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            insert_project = sql.SQL("insert into {table}({fields}) values (%s, %s, %s)") \
                .format(table=sql.Identifier('task'),
                        fields=sql.SQL(',').join([
                            sql.Identifier('name'),
                            sql.Identifier('project'),
                            sql.Identifier('team')
                        ]))
            cursor.execute(insert_project, (task, project, team))
            conn.commit()
    print(f"Создана задача: {task}, Команда: {team}, Проект: {project}")


def get_tasks(project, team):
    tasks = []

    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL("select {column} from {table} where {field1} = %s and {field2} = %s order by {column} asc") \
                .format(column=sql.Identifier('name'),
                        table=sql.Identifier('task'),
                        field1=sql.Identifier('project'),
                        field2=sql.Identifier('team'))
            cursor.execute(select, (project, team))
            for row in cursor:
                tasks.append(row['name'])
    return tasks


def get_task_status(project, team, task):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL("select {column} from {table} where {field1} = %s and {field2} = %s and {field3} = %s") \
                .format(column=sql.Identifier('status'),
                        table=sql.Identifier('task'),
                        field1=sql.Identifier('project'),
                        field2=sql.Identifier('team'),
                        field3=sql.Identifier('name'))
            cursor.execute(select, (project, team, task))
            return cursor.fetchone()['status']


def change_task_status(project, team, task, status):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            insert_project = sql.SQL(
                "update {table} set {column} = %s where {field1} = %s and {field2} = %s and {field3} = %s") \
                .format(column=sql.Identifier('status'),
                        table=sql.Identifier('task'),
                        field1=sql.Identifier('project'),
                        field2=sql.Identifier('team'),
                        field3=sql.Identifier('name'))
            cursor.execute(insert_project, (status, project, team, task))
            conn.commit()
    print(f"Изменен статус задачи: {task}, Команда: {team}, Проект: {project}, Новый статус: {status}")


def get_team_members(team):
    members = []

    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = sql.SQL(
                'select u."name" , u.id  from user_to_team utt join "user" u on utt.user_id  = u.id  where utt.team  = %s order by u.name asc') \
                # .format(table1=sql.Identifier('user_to_team'),
                #         shortname1=sql.Identifier('utt'),
                #         table2=sql.Identifier('user'),
                #         shortname2=sql.Identifier('u'),
                #         column=sql.Identifier('u.name'),
                #         columns=sql.SQL(',').join([
                #             sql.Identifier('u.id'),
                #             sql.Identifier('u.name'),
                #         ]),
                #         jfield1=sql.Identifier('user_id'),
                #         jfield2=sql.Identifier('u.id'),
                #         field=sql.Identifier('utt.team'),
                #         orfield=sql.Identifier('u.name'))
            cursor.execute(select, (team,))
            for row in cursor:
                members.append(row)
    return members


def delete_task(team, project, task):
    with closing(psycopg2.connect(dbname='PyOdysseyBot', user='postgres', password='admin', host='localhost')) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            delete_task = sql.SQL("delete from {table} where {field1} = %s and {field2} = %s and {field3} = %s") \
                .format(table=sql.Identifier('task'),
                        field1=sql.Identifier('team'),
                        field2=sql.Identifier('project'),
                        field3=sql.Identifier('name'))
            cursor.execute(delete_task, (team, project, task))
            conn.commit()
    print(f"Удалена задача: {task}")