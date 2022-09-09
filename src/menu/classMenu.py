from typing import List, Any, Tuple, Iterable, Callable

import interactions

from src.databasectl.postgres import PostgresQLDatabase, PostgresCursor
from src.reactionCallback.reactionCallbackManager import ReactionCallbackManager
from src.util.EmojiManager import create_managed_emote


class ClassMenu:
    def __init__(self, bot: interactions.Client, db: PostgresQLDatabase, ctx: interactions.CommandContext):
        self.bot = bot
        self.db = db
        self.ctx: interactions.CommandContext = ctx

    def _create_class_menu_group(
            self,
            menu_group_name,
            channel: interactions.Channel,
            menu_type="generic",
            description=None):
        with self.db.get_instance() as inst:
            inst.add_role_menu_group(menu_group_name, channel.id, menu_type, description=description)
        print(f"created class menu group '{menu_group_name}'")

    @staticmethod
    def _generate_embed_base(title, description=None):
        return interactions.Embed(
            title=title,
            description="react to the corresponding emoji to obtain role" if description is None else description)

    @staticmethod
    def _add_generate_menu_item(
            embed: interactions.Embed,
            name: str,
            emoji: interactions.Emoji,
            role: interactions.Role):
        embed.add_field(name=f"`{name}`",
                        value=f"{emoji} {' - ' * 45} {role.mention}"
                              f"\n\u2800",
                        inline=False)
        return embed

    @staticmethod
    def _add_generate_class_menu_item(
            embed: interactions.Embed,
            cls_name: str,
            emoji: interactions.Emoji,
            role: interactions.Role,
            inst: PostgresCursor):
        result = inst.get_all('CLASS', class_name=cls_name)
        full_name = result[0][1]
        embed.add_field(name=f"`{cls_name + ' (' + full_name + ')'}`",
                        value=f"{emoji} {' - ' * 45} {role.mention}"
                              f"\n\u2800",
                        inline=False)
        return embed

    async def generate_menu_from_group(
            self,
            menu_group_name,
            channel: interactions.Channel,
            names: List[str],
            roles: List[interactions.Role],
            emojis: List[interactions.Emoji],
            menu_type='generic',
            description="",
            item_limit=10):
        # do basic check on input
        if len(names) != len(emojis) or len(emojis) != len(roles):
            raise ValueError("classes, emojis, and roles don't have matching length")
        with self.db.get_instance() as inst:
            # generate the appropriate menu group
            self._create_class_menu_group(menu_group_name, channel, menu_type=menu_type, description=description)

            for index, i in enumerate(range(0, len(names), item_limit)):
                end = min(len(names), i + item_limit)
                lim_names, lim_emojis, lim_roles = names[i:end], emojis[i:end], roles[i:end]
                await self.generate_menu(
                    menu_group_name,
                    lim_names,
                    lim_roles,
                    lim_emojis,
                    inst,
                    menu_type=menu_type,
                    item_limit=item_limit,
                    index=index + 1)

    async def generate_menu(
            self,
            menu_group_name,
            names: List[str],
            roles: List[interactions.Role],
            emojis: List[interactions.Emoji],
            inst: PostgresCursor,
            menu_type='generic',
            item_limit=10,
            index=None):

        def generic_resolve(embed, name, role, emoji):
            self._add_generate_menu_item(embed, name, emoji, role)

        def class_resolve(embed, name, role, emoji):
            self._add_generate_class_menu_item(embed, name, emoji, role, inst)

        if menu_type.lower() == 'generic':
            resolve_content = generic_resolve
        elif menu_type.lower() == "class":
            resolve_content = class_resolve
        else:
            raise ValueError(f"unknown menu_type: '{menu_type}'")

        return await self._generate_menu(
            menu_group_name,
            [names, roles, emojis],
            resolve_content,
            lambda curs, menu_serial_id, name, role, emoji:
            curs.add_menu_entry(name, role.id, emoji, menu_serial_id),
            inst,
            item_limit=item_limit,
            index=index
        )

    async def add_menu_entry(self, menu_name, name: str, emoji, role: interactions.Role):
        with self.db.get_instance() as inst:
            if not inst.menu_group_exists(menu_name):
                raise ValueError(f"given menu group '{menu_name}' does not exist")
            menu_group = inst.get_all('ROLE_MENU_GROUP', group_name=menu_name)[0]
            _, channel_id, menu_type, description = menu_group
            menus = inst.get_all('ROLE_MENU', menu_group_name=menu_name)
            available_menu = None
            for menu in menus:
                menu_serial_id, msg_id, menu_group_name, item_limit = menu
                entries = inst.get_all('MENU_ENTRY', role_menu_id=menu_serial_id)
                if len(entries) < item_limit:
                    available_menu = menu
                    break

            if available_menu is None:
                # no menu available, create one
                menu_msg = \
                    await self.generate_menu(
                        menu_name,
                        [name], [role], [emoji],
                        inst,
                        menu_type=menu_type,
                        item_limit=item_limit,
                        index=len(menus) + 1)
                # menu_msg.crea
            else:
                inst.add_menu_entry(name, role.id, emoji, available_menu[0])
                channel = await interactions.get(self.bot, interactions.Channel, object_id=channel_id)
                msg = await channel.get_message(menu[1])
                embed = msg.embeds[0]
                if menu_type.lower() == 'generic':
                    self._add_generate_menu_item(embed, name, emoji, role)
                elif menu_type.lower() == "class":
                    self._add_generate_class_menu_item(embed, name, emoji, role, inst)
                await msg.edit(embeds=embed)
                # await msg.create_reaction(emoji)

    async def _generate_menu(
            self,
            menu_group_name,
            contents: List[List[Any]],
            resolve_content: Callable[[interactions.Embed, Any], Any],
            resolve_database: Callable[[PostgresCursor, int, Any], Any],
            inst: PostgresCursor,
            item_limit=10,
            index=None):
        # just to make sure they are all the same size
        zipped_result: Iterable[Tuple[Any]] = zip(contents, strict=True)
        if len(contents) == 0:
            raise ValueError("empty content, this is pointless")
        if len(contents[0]) > item_limit:
            raise ValueError(f"expected all item to have size less than or equal to {item_limit}, "
                             f"however got size {len(contents[0])}")
        # generate the menu msg
        menu_group = inst.get_all('ROLE_MENU_GROUP', args=['group_name', 'menu_type', 'description', 'channel_id'],
                                  group_name=menu_group_name)[0]
        _, menu_type, description, channel_id = menu_group
        print(f'getting channel with id "{channel_id}"')
        channel = await interactions.get(self.bot, interactions.Channel, object_id=int(channel_id))
        msg = await channel.send("building...")
        embed_name = menu_group_name if index is None else menu_group_name + f": part {index}"
        menu_embed = self._generate_embed_base(embed_name, description=description)

        if not inst.menu_group_exists(menu_group_name):
            raise ValueError(f"the menu group '{menu_group_name}' does not exist")

        # add the role menu to database
        menu_serial_id = inst.add_role_menu(msg.id, menu_group_name, item_limit=item_limit)
        for j in range(len(contents[0])):
            item_lists = [li[j] for li in contents]
            # add the ui embed
            resolve_content(menu_embed, *item_lists)
            # add to database
            resolve_database(inst, menu_serial_id, *item_lists)

        await msg.edit("", embeds=menu_embed)
        return msg

    async def load_menu(
            self,
            menu_name: str,
            log_channel: interactions.Channel,
            guild_id,
            callbackManager: ReactionCallbackManager):
        with self.db.get_instance() as inst:
            if not inst.menu_group_exists(menu_name):
                raise ValueError(f"menu group {menu_name} does not exist yet, consider creating it instead of loading")
            _, channel_id, _, _ = inst.get_all(
                'ROLE_MENU_GROUP',
                args=['group_name', 'channel_id', 'menu_type', 'description'],
                group_name=menu_name)[0]
            print(f'menu "{menu_name}" exists, proceed with menu loading')
            print(f"fetching channel '{channel_id}', guild '{guild_id}'")
            channel = await interactions.get(self.bot, interactions.Channel, object_id=int(channel_id))
            guild = await interactions.get(self.bot, interactions.Guild, object_id=int(channel.guild_id))
            menus = inst.get_all(
                'ROLE_MENU',
                menu_group_name=menu_name
            )
            print(f'starting load, sending a message to log channel for emoji...')
            emoji_msg = await log_channel.send("testing emojis ...")
            print(f'message sent, now go forward')
            bot_id = self.bot.me.id
            for menu_id, msg_id, _, _ in menus:
                msg = await channel.get_message(msg_id)
                entries = inst.get_all('MENU_ENTRY', role_menu_id=menu_id)
                # ensure we are reacting in order
                entries.sort(key=lambda x: x[0])
                for _, entry_name, role_id, emoji, _ in entries:
                    # emoji resolution
                    emoji: interactions.Emoji = \
                        await create_managed_emote(emoji, guild, log_channel, existing_msg=emoji_msg)
                    print(f'role id: {role_id}, {emoji}')

                    def add_role(role_id):
                        async def func(reaction: interactions.MessageReaction):
                            if reaction.user_id == bot_id:
                                return
                            print(f"detected, adding role {role_id}")
                            # user = await interactions.get(self.bot, interactions.User, object_id=int(
                            # reaction.user_id))
                            await reaction.member.add_role(role_id, guild_id, reason="on react add")

                        return func

                    def remove_role(role_id):
                        async def func(reaction: interactions.MessageReaction):
                            if reaction.user_id == bot_id:
                                return
                            print(f"detected, removing role {role_id}")
                            try:
                                guild: interactions.Guild = \
                                    await interactions.get(self.bot, interactions.Guild,
                                                           object_id=int(reaction.guild_id))
                                member = await guild.get_member(reaction.user_id)
                                await member.remove_role(role_id, self.ctx.guild_id, reason="on react remove")
                            except Exception:
                                print(f"member removed emoji {reaction.emoji}, "
                                      f"however does not have the role")

                        return func

                    callbackManager.add_reaction_emoji_callback(msg_id, emoji, add_role(role_id), remove_role(role_id))
                    await msg.create_reaction(emoji)
                    # print(entry_name, role_id, emoji)
            # pprint.pprint(callbackManager.emoji_callbacks)
            await emoji_msg.delete("testing emoji message not released")
