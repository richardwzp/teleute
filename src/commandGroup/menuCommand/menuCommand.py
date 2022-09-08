from typing import Dict

import interactions

from src.databasectl.dataRead import readPreset
from src.databasectl.postgres import PostgresQLDatabase
from src.menu.classMenu import ClassMenu
from src.reactionCallback.reactionCallbackManager import ReactionCallbackManager
from src.util.decorateString import MutableMessage

from Config import get_server_id

gl_private_guild_id = get_server_id()
default_emos = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class MenuCommand(interactions.Extension):
    def __init__(self, client, db: PostgresQLDatabase, callback: ReactionCallbackManager):
        self.bot = client
        self.db = db
        self.callback = callback

    @interactions.extension_command(
        name="preset_class",
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
    async def preset_class(self, ctx: interactions.CommandContext):
        await ctx.send("started preset")
        data = readPreset('databasectl/classPreset.yaml')
        guild = await ctx.get_guild()
        all_roles: Dict[str, interactions.Role] = {role.name: role for role in await guild.get_all_roles()}

        names, full_names, roles, emojis = [], [], [], ['😄', '😀', '😃', '🥶', '😁', '😆', '😅',
                                                        '😂', '🤣', '☺', '🥳', '🥰', '😍', '🥲', '😌', '😉', '🙃'][:12]
        ta_roles = {}
        for val in data:
            class_name, full_name, description, school = val.values()
            class_name = class_name.upper()
            names.append(class_name)
            roles.append(all_roles[class_name])
            full_names.append(full_name)
            ta_roles[class_name] = all_roles[class_name + " TA"]

        menu = ClassMenu(self.bot, self.db, ctx)
        # await menu.generate_menu_from_group('group1', await ctx.get_channel(), names, roles, emojis, item_limit=3)
        await menu.generate_menu_from_group(
            'Fall 2022 classes', await ctx.get_channel(), names, roles, emojis, menu_type='class', item_limit=6)

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
        msgBuilder = MutableMessage(
            ctx, initial_message="adding menu entries...\n").surround_default_codeBlock(lang="diff")
        await msgBuilder.send()
        menu = ClassMenu(self.bot, self.db, ctx)
        await menu.add_menu_entry(menu_name, name, emoji, role)
        await msgBuilder.add_text("+ adding finished\n").send()
        await msgBuilder.add_text("reloading all reactions...\n").send()
        await self.load_menu(ctx, menu_name, no_trace=True)
        await msgBuilder.ctxMsg.delete()

    @interactions.extension_command(
        name="load_menu",
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
        ],
    )
    async def load_menu(self, ctx: interactions.CommandContext, menu_name, no_trace=False):
        msg1 = await ctx.send("staring menu loading...")
        await ClassMenu(self.bot, self.db, ctx).load_menu(menu_name, await ctx.get_channel(), self.callback)
        msg2 = await ctx.send("done")
        if no_trace:
            await msg1.delete()
            await msg2.delete()


def setup(client, db, cb_manager):
    MenuCommand(client, db, cb_manager)