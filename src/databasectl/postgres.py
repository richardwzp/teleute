from contextlib import AbstractContextManager
from types import TracebackType
from typing import Type
from psycopg2._psycopg import connection, cursor

import psycopg2


def error_proof(log=print):
    def outer_wrapper(func):
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
                return True
            except Exception as e:
                log(str(e))
                return False

        return wrapper
    return outer_wrapper


class PostgresQLDatabase(AbstractContextManager):
    def __exit__(self, __exc_type: Type[BaseException] | None, __exc_value: BaseException | None,
                 __traceback: TracebackType | None) -> bool | None:
        return self.conn.close()

    def __init__(self, host, database, user, password, log=print):
        self.conn: connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password)
        self.log = log

    def get_instance(self):
        return PostgresCursor(self)


class PostgresCursor(AbstractContextManager):
    def __exit__(self, __exc_type: Type[BaseException] | None, __exc_value: BaseException | None,
                 __traceback: TracebackType | None) -> bool | None:
        # if there is no error, commit this
        if __exc_type is None:
            self.db.conn.commit()

        return self.cursor.close()

    def __init__(self, db: PostgresQLDatabase, log=print):
        self.db = db
        self.cursor: cursor = self.db.conn.cursor()
        self.log = log

    def commit(self):
        self.db.conn.commit()
        self.cursor.close()
        self.cursor = self.db.conn.cursor()

    def get_all(self, cls_name, **kwargs):
        self.cursor.execute(
            f'SELECT * FROM {cls_name} '
            f'WHERE {"AND ".join([f"{i.upper()}=%s" for i in kwargs])}',
            tuple(kwargs.values())
        )
        return self.cursor.fetchall()

    def menu_group_exists(self, menu_group_name: str):
        return len(self.get_all('ROLE_MENU_GROUP', group_name=menu_group_name)) != 0

    def how_many_menu_entry(self, role_menu_id: int):
        return len(self.get_all('MENU_ENTRY', role_menu_id=int(role_menu_id)))


    def add_class(self, class_name: str, full_name: str, description: str, school: str):
        """
        adding a class to the databasectl. this is not committed immediately.
        :param class_name: the name of the class (ie: CS2500) case will be auto uppercase
        :param full_name: the full name of the class
        :param description: a description of the class, can be left as an empty string.
        :param school: the school, in abbreviation, this will be auto uppercase
        :return: if adding the class succeeded
        """
        self.cursor.execute(
            'INSERT INTO CLASS (CLASS_NAME, FULL_NAME, DESCRIPTION, SCHOOL) VALUES (%s, %s, %s, %s)',
            (class_name.upper(), full_name, description, school.upper()))

    def add_menu_entry(self, entry_name, role_id, emoji, role_menu_id):
        """
        Add a menu entry, this is not committed immediately.
        :param entry_name: the name of the entry
        :param role_id: the role id
        :param emoji: the emoji connected
        :param role_menu_id: the id of the role menu
        :return: the entry id
        """
        self.cursor.execute(
            'INSERT INTO MENU_ENTRY (ENTRY_NAME, ROLE_ID, EMOJI, ROLE_MENU_ID) VALUES (%s, %s, %s, %s)',
            (entry_name, str(role_id), emoji, int(role_menu_id)))
        return self.get_all(
            "MENU_ENTRY",
            entry_name=entry_name,
            role_id=str(role_id),
            emoji=emoji,
            role_menu_id=int(role_menu_id))[0][0]

    def add_class_menu_entry(self, entry_id, class_name):
        """
        Add a menu entry class, this is not committed immediately.
        :param entry_id: the id of the menu entry
        :param class_name: the name of the class
        :return: if the add succeeded
        """
        self.cursor.execute(
            'INSERT INTO MENU_ENTRY_CLASS (ENTRY_ID, CLASS_NAME) VALUES (%s, %s)',
            (int(entry_id), class_name))

    def add_role_menu(self, message_id, menu_group_name, item_limit):
        """
        add a role menu, this is not committed immediately.
        :param message_id: the id of the message
        :param menu_group_name: the name of the menu group this menu belongs to
        :param item_limit: how many item this menu can hold
        :return: if the add succeeded
        """
        self.cursor.execute(
            'INSERT INTO ROLE_MENU (MESSAGE_ID, MENU_GROUP_NAME, item_limit) VALUES (%s, %s, %s)',
            (str(message_id), menu_group_name, int(item_limit)))

        return self.get_all(
            "ROLE_MENU",
            message_id=str(message_id),
            menu_group_name=menu_group_name,
            item_limit=item_limit)[0][0]

    def add_role_menu_group(self, group_name, channel_id, menu_type, description=""):
        """
        add a role menu group, this is not committed immediately.
        :param group_name: the name of the menu group
        :param channel_id: the id of the channel this role menu is in.
        :param menu_type: the type of the menu. It's either CLASS or GENERIC.
        :param description: a descritpion of the menu group, default to empty string.
        :return: if the add succeeded
        """
        self.cursor.execute(
            'INSERT INTO ROLE_MENU_GROUP (GROUP_NAME, CHANNEL_ID, MENU_TYPE, DESCRIPTION) VALUES (%s, %s, %s, %s)',
            (group_name, str(channel_id), menu_type, description))
















if __name__ == '__main__':
    with PostgresQLDatabase() as db:

        with PostgresQLDatabase().get_instance() as inst:
            print(inst.get_all("role_menu_group", group_name="group", channel_id="838844818842583101"))





