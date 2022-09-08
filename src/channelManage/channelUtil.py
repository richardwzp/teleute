import interactions
import random

from src.util.decorateString import MutableMessage


def rbe():
    return random.Random().randint(0, 255)


class ChannelUtil:
    def __init__(self, ctx: interactions.CommandContext):
        self.ctx = ctx

    @staticmethod
    def is_category(channel: interactions.Channel):
        return channel.type == interactions.ChannelType.GUILD_CATEGORY

    @staticmethod
    def create_read_write_thread_permission(role_id):
        # must be serialized here, else there will be esoteric json error
        role_id = int(role_id)
        perms = [
            interactions.Overwrite(
                id=role_id,
                type=0,
                allow=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.CREATE_PUBLIC_THREADS)]
        # disallow everyone to see, and allow specific role to send read messages, and create public thread
        return perms

    @staticmethod
    def create_no_view_permission(role_id, ta_role_id, guild_id):
        # must be serialized here, else there will be esoteric json error
        role_id = int(role_id)
        ta_role_id = int(ta_role_id)
        guild_id = int(guild_id)
        perms = [
            interactions.Overwrite(
                id=role_id,
                type=0,
                deny=interactions.Permissions.VIEW_CHANNEL),
            interactions.Overwrite(
                id=ta_role_id,
                type=0,
                allow=interactions.Permissions.VIEW_CHANNEL),
            interactions.Overwrite(
                id=guild_id,
                type=0,
                deny=interactions.Permissions.VIEW_CHANNEL)
        ]
        return perms

    @staticmethod
    def hide_from_everyone_permission(iid):
        # must be serialized here, else there will be esoteric json error
        iid = int(iid)
        return [interactions.Overwrite(id=iid, type=0, deny=interactions.Permissions.VIEW_CHANNEL)]

    @staticmethod
    def no_view_and_read_only_permission(iid):
        # must be serialized here, else there will be esoteric json error
        iid = int(iid)
        return [interactions.Overwrite(
            id=iid,
            type=0,
            deny=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES)]

    async def createRole(self, cls_name: str, color=None):
        guild = await self.ctx.get_guild()
        color = color if color is not None else int('%02x%02x%02x' % (rbe(), rbe(), rbe()), 16)
        role = await guild.create_role(cls_name, color=color)
        return role, color

    async def createClass(self, cls_name: str):
        recordMsg = MutableMessage(self.ctx).surround_default_codeBlock("diff")
        await recordMsg.add_text(f"Creating class {cls_name}:\n").send()
        guild = await self.ctx.get_guild()
        role, role_color = await self.createRole(cls_name)
        await recordMsg.add_text(f"+ created role {cls_name}\n").send()
        ta_role, _ = await self.createRole(cls_name + " TA", color=role_color)
        await recordMsg.add_text(f"+ created role {cls_name + ' TA'}\n").send()

        everyone_perms = self.hide_from_everyone_permission(guild.id)
        role_perms = self.create_read_write_thread_permission(role.id)
        # no_view_and_read_only_perm = self.no_view_and_read_only_permission(guild.id)

        category = await guild.create_channel(cls_name, interactions.ChannelType.GUILD_CATEGORY)
        await recordMsg.add_text(f"+ created category '{cls_name}'\n").send()
        await category.modify(permission_overwrites=everyone_perms + role_perms)
        await recordMsg.add_text(f"+ modified permission for category '{cls_name}'\n").send()

        await guild.create_channel("announcement",
                                   interactions.ChannelType.GUILD_TEXT,
                                   parent_id=category,
                                   rate_limit_per_user=1800)
        await recordMsg.add_text(f"+ created channel 'announcement'\n").send()

        # await an_ch.modify(permission_overwrites=no_view_and_read_only_perm + role_perms)
        # await recordMsg.add_text(f"+ modified 'announcement' to be read only\n").send()

        await guild.create_channel("general", interactions.ChannelType.GUILD_TEXT, parent_id=category)
        await recordMsg.add_text(f"+ created channel 'general'\n").send()

        ta_chat = await guild.create_channel("ta-chat", interactions.ChannelType.GUILD_TEXT, parent_id=category)
        ta_perm = self.create_no_view_permission(role.id, ta_role.id, guild.id)
        recordMsg.add_text(f"+ created something for the TAs ...\n")
        await ta_chat.modify(permission_overwrites=ta_perm)

        await guild.create_channel("study group 1", interactions.ChannelType.GUILD_VOICE, parent_id=category)
        await recordMsg.add_text(f"+ created voice channel 'study group 1'\n").send()

        await guild.create_channel("study group 2", interactions.ChannelType.GUILD_VOICE, parent_id=category)
        await recordMsg.add_text(f"+ created voice channel 'study group 2'\n").send()

        await recordMsg.add_text(f"@ creation done @").send()
