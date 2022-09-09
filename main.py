import sys
from typing import Optional
import configparser

import interactions

from Config import get_server_id
from src.commandGroup.menuCommand.menuCommand import _MenuCommand
from src.commandGroup.profCommand.profCommand import ProfCommand, _ProfCommand
from src.databasectl.postgres import PostgresQLDatabase, PostgresCursor
from src.menu.classMenu import ClassMenu
from src.menu.menuUtil import get_all_menu
from src.reactionCallback.reactionCallbackManager import ReactionCallbackManager

cfg = configparser.ConfigParser()
cfg.read('secret.cfg')
d = cfg['database']
token, host, database, user, password = cfg['server']['token'], d['host'], d['database'], d['user'], d['password']

if len(sys.argv) > 1:
    deploy_status = sys.argv[1].lower()
    if deploy_status not in {'dev', 'prd'}:
        raise ValueError(f'expected "dev" or "prd", got {deploy_status} instead')
else:
    deploy_status = 'dev'

# print(token, host, database, user, password)
intents = interactions.Intents.DEFAULT \
          | interactions.Intents.GUILD_MESSAGES | interactions.Intents.GUILD_MEMBERS
bot = interactions.Client(token=token, intents=intents)

db: Optional[PostgresQLDatabase] = None
callback_manager = ReactionCallbackManager(bot)
default_emos = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@bot.event
async def on_message_reaction_add(reaction: interactions.MessageReaction):
    print('reacted to')
    # guild = await interactions.get(bot, interactions.Guild, object_id=int(reaction.guild_id))
    await callback_manager.process_add_reaction(reaction)


@bot.event
async def on_raw_message_reaction_remove(reaction: interactions.MessageReaction):
    print(reaction.message_id)
    guild: interactions.Guild = await interactions.get(bot, interactions.Guild, object_id=int(reaction.guild_id))
    member = await guild.get_member(reaction.user_id)
    print('happened', member)
    await callback_manager.process_remove_reaction(reaction)


@bot.event
async def on_ready():
    s = deploy_status
    print(f"-- sandman is ready ---")
    print(f"--       {s}        ---")
    guilds = bot.guilds
    channels = {}

    async def get_all_channels():
        raw_channels = []
        for guild in guilds:
            raw_channels.extend(await guild.get_all_channels())

        for channel in raw_channels:
            channels[channel.id] = channel

    with db.get_instance() as inst:
        menu_groups = get_all_menu(inst)
        for group_name, channel_id, menu_type, description in menu_groups:
            print(f"fetching channel '{channel_id}'")
            if len(channels) > 0:
                channel = channels[channel_id]
            else:
                channel = await interactions.get(bot, interactions.Channel, object_id=channel_id)
                if channel.guild_id is None:
                    print('channel has no guild_id, brute force to get a good channel obj')
                    await get_all_channels()
                    channel = channels[channel_id]


            # TODO: ctx is not needed here. This is a hack, ClassMenu should not depend on context
            await ClassMenu(bot, db, None).load_menu(group_name, channel, channel.guild_id, callback_manager)


try:
    db = PostgresQLDatabase(host, database, user, password, lib_type='jdbc')
    bot.load('src.commandGroup.menuCommand.menuCommand', db=db, cb_manager=callback_manager)
    bot.load('src.commandGroup.channelCommand.channelCommand', db=db, cb_manager=callback_manager)
    bot.load('src.commandGroup.classCommand.classCommand', db=db, cb_manager=callback_manager)
    bot.load('src.commandGroup.profCommand.profCommand')
    bot.load('src.commandGroup.miscCommand.miscCommand')
    bot.start()
except Exception as e:
    print(str(e))
    db.__exit__(type(e), e, e.__traceback__)
