import json
import re
from collections import defaultdict
from io import StringIO
from typing import Dict, Optional, List

import interactions
import yaml

from Config import get_server_id, get_fall_2021, store_in_root_name
from src.channelManage.channelUtil import ChannelUtil
from src.databasectl.postgres import PostgresQLDatabase
from src.reactionCallback.reactionCallbackManager import ReactionCallbackManager
from src.util.decorateString import MutableMessage
from src.util.getter import RoleGetter

gl_private_guild_id = get_server_id()
default_emos = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class _ChannelCommand:
    def __init__(self, client, db: PostgresQLDatabase, callback: ReactionCallbackManager):
        self.bot = client
        self.db = db
        self.callback = callback

    @interactions.extension_command(
        name="clean_all",
        description="clear out all channel",
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
    async def clean_all(self, ctx: interactions.CommandContext):
        #
        # assumptions: all category name must be in the format of abbreviation plus class number. ie: 'CS2500'
        # assumptions: all role has the same name and case as the category name, and all roles of that name
        #              must be deleted
        # assumptions: all channel under will be deleted
        #
        guild = await ctx.get_guild()
        channels = await guild.get_all_channels()
        roleManager = RoleGetter(ctx)

        category: Dict[Optional[interactions.Snowflake], List[interactions.Channel]] = defaultdict(lambda: [])
        # create a dictionary of category_id -> channel. channel without an id will be under None
        for channel in channels:
            category[channel.parent_id].append(channel)
        category_msgs: Dict[interactions.Snowflake, MutableMessage] = {}
        # loop through all possible categories
        for category_model in category[None]:
            # if the channel is a category, and if it's in the format of a class
            if ChannelUtil.is_category(category_model) and re.match(r"^[a-zA-Z]+\d{4}$", category_model.name):
                # set up the message that will track this category of deletion
                if category_model.id not in category_msgs:
                    category_msgs[category_model.id] = MutableMessage(ctx).surround_default_codeBlock(lang="diff")
                    category_msgs[category_model.id].add_text(f"Now deleting category '{category_model.name}'\n")
                    # delete the role and acknowledge it
                    to_be_deleted_roles = await roleManager.getRole(category_model.name)
                    # delete the ta roles also
                    to_be_deleted_roles.extend(await roleManager.getRole(category_model.name + " TA"))
                    category_msgs[category_model.id].add_text(f"- deleted {len(to_be_deleted_roles)} role\n")
                    for role in to_be_deleted_roles:
                        await role.delete(guild.id, "role deleted as part of clear all")

                deleteMsg = category_msgs[category_model.id]
                channels = category[category_model.id]
                await deleteMsg.send()
                for channel in channels:
                    await deleteMsg.add_text(f"- deleted channel {channel.name}\n").send()
                    await channel.delete()
                await category_model.delete()
                deleteMsg.add_text("-- all deleted --")

        await ctx.send("all deletions are done.")

    # @bot.modal("class_name")
    # async def modal_response(ctx: interactions.CommandContext, response: str):
    #     await ctx.send(f"You wrote: {response}", ephemeral=True)

    # modal = interactions.Modal(
    #     title="Application Form",
    #     custom_id="class_name",
    #     components=[
    #         interactions.TextInput(
    #             style=interactions.TextStyleType.SHORT,
    #             label="class name",
    #             custom_id="class_name")],
    # )

    @interactions.extension_command(
        name="scan_class",
        description="scan over all content inside of the current channel",
        scope=gl_private_guild_id,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    )
    async def scan_class(self, ctx: interactions.CommandContext):
        channel = await ctx.get_channel()
        msgs = await channel.get_history(limit=500)
        classes = []
        for msg in msgs:
            if "full_name:" not in msg.content:
                continue
            if "ie" in msg.content:
                continue

            content = msg.content.strip("```yaml").strip("```text").strip("```")
            content.strip("```")
            dic = yaml.safe_load(StringIO(content))
            if 'description' not in dic:
                dic['description'] = ""

            for i in dic:
                if isinstance(dic[i], list):
                    dic[i] = dic[i][0]
            dic['class_name'] = dic['name']
            del dic['name']
            dic['class_name'] = "".join(dic['class_name'].split(" "))
            classes.append(dic)

        fall = get_fall_2021()
        keep = {}

        for i in classes + fall:
            # print(i)
            class_name, _, _ = i['class_name'], i['full_name'], i['description']
            keep[class_name] = i

        # res = "\n".join([str(i) for i in keep.values()])
        result = sorted(list(keep.values()), key=lambda x: x['class_name'])
        with open(store_in_root_name('preset.json'), "w") as f:
            json.dump(result, f)

        await ctx.send(f'stored')


class ChannelCommand(_ChannelCommand, interactions.Extension):
    def __init__(self, client, db: PostgresQLDatabase, callback: ReactionCallbackManager):
        super().__init__(client, db, callback)


def setup(client, db, cb_manager):
    ChannelCommand(client, db, cb_manager)
