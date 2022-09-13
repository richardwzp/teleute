import json
from typing import Dict

import interactions

from src.channelManage.channelUtil import ChannelUtil
from src.databasectl.dataRead import readPreset
from src.databasectl.postgres import PostgresQLDatabase
from src.menu.classMenu import ClassMenu
from src.reactionCallback.reactionCallbackManager import ReactionCallbackManager
from src.util.decorateString import MutableMessage

from Config import get_server_id, PRESET_PATH

gl_private_guild_id = get_server_id()
default_emos = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class _MenuCommand:
    def __init__(self, client: interactions.Client, db: PostgresQLDatabase, callback: ReactionCallbackManager):
        self.bot = client
        self.db = db
        self.callback = callback

    @interactions.extension_command(
        name="populate_database_class",
        description="populate the database with some preset classes, this should only be run once",
        scope=gl_private_guild_id,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        # options=[
        #     interactions.Option(
        #         name="channel",
        #         description="the channel name",
        #         type=interactions.OptionType.CHANNEL,
        #         required=True,
        #     ),
        # ],
    )
    async def populate_database_class(self, ctx: interactions.CommandContext):
        await ctx.send("started database population")
        with open('preset.json') as f:
            data = json.loads(f.read())
            for dic in data:
                dic['school'] = "NEU"
        with self.db.get_instance() as inst:
            for val in data:
                class_name, full_name, description, school = \
                    val["class_name"], val["full_name"], val["description"], val["school"]
                inst.add_class(class_name, full_name, description, school)
                await ChannelUtil(ctx).createClass(class_name.upper())

    @interactions.extension_command(
        name="create_preset_class",
        description="create resource for all preset classes",
        scope=gl_private_guild_id,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        # options=[
        #     interactions.Option(
        #         name="channel",
        #         description="the channel name",
        #         type=interactions.OptionType.CHANNEL,
        #         required=True,
        #     ),
        # ],
    )
    async def create_preset_class(self, ctx: interactions.CommandContext):
        await ctx.send("started preset")
        print('start successfully')
        with open(PRESET_PATH) as f:
            data = json.loads(f.read())
            for dic in data:
                dic['school'] = "NEU"
        print('opened successfully')
        guild = await ctx.get_guild()
        all_roles: Dict[str, interactions.Role] = {role.name: role for role in await guild.get_all_roles()}

        names, full_names, roles, emojis = [], [], [], default_emos
        # ['😄', '😀', '😃', '🥶', '😁', '😆', '😅', '😂', '🤣', '☺', '🥳', '🥰', '😍', '🥲', '😌', '😉', '🙃'][:12]
        ta_roles = {}
        print('start menu generation')
        for val in data:
            class_name, full_name, description, school = \
                val["class_name"], val["full_name"], val["description"], val["school"]
            class_name = class_name.upper()
            names.append(class_name)
            roles.append(all_roles[class_name])
            full_names.append(full_name)
            ta_roles[class_name] = all_roles[class_name + " TA"]

        def get_emoji():
            while True:
                emo_iter = iter(emojis)
                for emo in emo_iter:
                    yield emo

        emo_iter = iter(get_emoji())
        emojis = [next(emo_iter) for _ in names]
        menu = ClassMenu(self.bot, self.db, ctx)
        # await menu.generate_menu_from_group('group1', await ctx.get_channel(), names, roles, emojis, item_limit=3)
        await menu.generate_menu_from_group(
            'Fall 2022 classes', await ctx.get_channel(), names, roles, emojis, menu_type='class', item_limit=10)

    @interactions.extension_command(
        name="add_menu_entry",
        description="load the menu",
        scope=gl_private_guild_id,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        options=[
            interactions.Option(
                name="menu_name",
                description="the name of the menu",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="name",
                description="the name to be linked to the react",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="emoji",
                description="emoji to be used",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="role",
                description="the role associated",
                type=interactions.OptionType.ROLE,
                required=True,
            ),
        ],
    )
    async def add_menu_entry(self, ctx: interactions.CommandContext, menu_name, name, emoji, role: interactions.Role):
        with self.db.get_instance() as inst:
            msgBuilder = MutableMessage(
                ctx, initial_message="adding menu entries...\n").surround_default_codeBlock(lang="diff")
            await msgBuilder.send()
            menu = ClassMenu(self.bot, self.db, ctx)
            await menu.add_menu_entry(inst, menu_name, name, emoji, role, self.callback)
            await msgBuilder.add_text("+ adding finished\n").send()
            await msgBuilder.add_text("reloading all reactions...\n").send()
            await menu.load_class(inst, name, self.callback)
            await msgBuilder.ctxMsg.delete()

    @interactions.extension_command(
        name="loading_menu",
        description="load the menu",
        scope=gl_private_guild_id,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        options=[
            interactions.Option(
                name="menu_name",
                description="the name of the menu",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="no_trace",
                description="should the command leave no message from the bot",
                type=interactions.OptionType.STRING,
                required=False,
            ),
        ],
    )
    async def loading_menu(self, ctx: interactions.CommandContext, menu_name, no_trace=False):
        msg1 = await ctx.send("staring menu loading...")
        await ClassMenu(self.bot, self.db, ctx).\
            load_menu(menu_name, await ctx.get_channel(), ctx.guild_id, self.callback)
        msg2 = await ctx.send("done")
        if no_trace:
            await msg1.delete()
            await msg2.delete()


class MenuCommand(_MenuCommand, interactions.Extension):
    def __init__(self, client: interactions.Client, db: PostgresQLDatabase, callback: ReactionCallbackManager):
        super().__init__(client, db, callback)


def setup(client, db, cb_manager):
    MenuCommand(client, db, cb_manager)
