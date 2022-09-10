from src.databasectl.postgres import PostgresCursor


def get_all_menu(inst: PostgresCursor):
    menus = inst.get_all(
        'ROLE_MENU_GROUP',
        args=['group_name',
              'channel_id',
              'menu_type',
              'description',
              'guild_id'])
    return menus

