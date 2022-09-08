from typing import Dict, Tuple

import interactions


class ReactionCallbackManager:
    def __init__(self, bot: interactions.Client):
        self.emoji_callbacks: Dict[str, Dict[str, Tuple]] = {}
        self.bot = bot

    def should_fire(self, reactions: interactions.MessageReaction) -> bool:
        return \
            (str(reactions.message_id) in self.emoji_callbacks) and \
            (str(reactions.emoji) in self.emoji_callbacks[str(reactions.message_id)])

    async def process_add_reaction(self, reactions: interactions.MessageReaction):
        if self.should_fire(reactions):
            print(str(reactions.message_id), str(reactions.emoji))
            await self.emoji_callbacks[str(reactions.message_id)][str(reactions.emoji)][0](reactions)

    async def process_remove_reaction(self, reactions: interactions.MessageReaction):
        if self.should_fire(reactions):
            print(str(reactions.message_id), str(reactions.emoji))
            await self.emoji_callbacks[str(reactions.message_id)][str(reactions.emoji)][1](reactions)

    def add_reaction_emoji_callback(self, msg_id, emoji, add_role, del_role):
        if str(msg_id) not in self.emoji_callbacks:
            self.emoji_callbacks[str(msg_id)] = {}
        self.emoji_callbacks[str(msg_id)][str(emoji)] = (add_role, del_role)
