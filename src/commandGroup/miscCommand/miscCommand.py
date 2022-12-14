import interactions
from interactions import extension_command

from Config import get_server_id

# set to null when goes global
guild_id = get_server_id()


class _MiscCommand:
    def __init__(self, client):
        self.bot = client

    @extension_command(name="algo_discord", description="""
    send the link for the algo_discord
    """, scope=guild_id)
    async def algo(self, ctx: interactions.CommandContext):
        await ctx.send('https://discord.gg/eteUMkvYtG')


class MiscCommand(_MiscCommand, interactions.Extension):
    def __init__(self, client):
        super().__init__(client)


def setup(client):
    MiscCommand(client)
