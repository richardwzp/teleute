import sys
from typing import Optional
import configparser

import interactions

from src.databasectl.postgres import PostgresQLDatabase, PostgresCursor
from src.reactionCallback.reactionCallbackManager import ReactionCallbackManager

token = sys.argv[1]
host, database, user, password = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]

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
    print("-- sandman is ready ---")
    print("--       dev        ---")


try:
    db = PostgresQLDatabase(host, database, user, password, lib_type='jdbc')
    bot.load('src.commandGroup.menuCommand.menuCommand', db=db, cb_manager=callback_manager)
    bot.load('src.commandGroup.channelCommand.channelCommand', db=db, cb_manager=callback_manager)
    bot.load('src.commandGroup.classCommand.classCommand', db=db, cb_manager=callback_manager)
    bot.load('src.commandGroup.profCommand.profCommand')
    bot.start()
except Exception as e:
    print(str(e))
    db.__exit__(type(e), e, e.__traceback__)
