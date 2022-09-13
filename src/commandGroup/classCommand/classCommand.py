import re

import interactions

from Config import get_server_id
from src.channelManage.channelUtil import ChannelUtil
from src.databasectl.postgres import PostgresQLDatabase
from src.reactionCallback.reactionCallbackManager import ReactionCallbackManager
from src.util.decorateString import MutableMessage

gl_private_guild_id = get_server_id()
default_emos = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class _ClassCommand:
    def __init__(self, client, db: PostgresQLDatabase, callback: ReactionCallbackManager):
        self.bot = client
        self.db = db
        self.callback = callback

    async def create_class_resource(self, ctx: interactions.CommandContext, class_name: str):
        await ChannelUtil(ctx).createClass(class_name.upper())
        # await ctx.send(f"all creation done for class '{class_name.upper()}'")

    @interactions.extension_command(
        name="create_class",
        description="create a category, generate related channels, persist the data, and create roles",
        scope=gl_private_guild_id,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        options=[
            interactions.Option(
                name="class_name",
                description="the class name formatted like CS2500",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="full_name",
                description="the full name of the class",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="school",
                description="the school name",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="description",
                description="the description of the class",
                type=interactions.OptionType.STRING,
                required=False,
            ),
        ],
    )
    async def create_class(self, ctx: interactions.CommandContext, class_name: str, full_name, school, description=""):
        with self.db.get_instance() as inst:
            inst.add_class(class_name, full_name, description, school)

        msg = MutableMessage(ctx, initial_message="+ created class successfully."). \
            surround_default_codeBlock(lang="diff")
        await msg.send()

        await self.create_class_resource(ctx, class_name)

    @interactions.extension_command(
        name="clear_class_roles",
        description="clear out all the class roles, including TA roles",
        scope=gl_private_guild_id,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    )
    async def clear_class_roles(self, ctx: interactions.CommandContext):
        guild = await ctx.get_guild()
        all_roles = await guild.get_all_roles()
        roleMsg = MutableMessage(ctx)
        roleMsg.surround_default_codeBlock(lang="diff")
        roleMsg.add_text("Deleting all class related Roles:\n")
        await roleMsg.send()

        for role in all_roles:
            if re.match(r"^[a-zA-Z]+\d{4}( TA)?$", role.name):
                roleMsg.add_text(f"- deleted role {role.name}\n")
                await role.delete(guild.id, reason="mass deleting roles through role delete command")
                await roleMsg.send()
        await ctx.send("all role deletion finished")


class ClassCommand(_ClassCommand, interactions.Extension):
    def __init__(self, client, db: PostgresQLDatabase, callback: ReactionCallbackManager):
        super().__init__(client, db, callback)


def setup(client, db, cb_manager):
    ClassCommand(client, db, cb_manager)
