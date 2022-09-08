from typing import List

import interactions


class RoleGetter:
    def __init__(self, ctx: interactions.CommandContext):
        self.roles = None
        self.ctx = ctx

    async def getRole(self, role_name) -> List[interactions.Role]:
        if self.roles is None:
            guild = await self.ctx.get_guild()
            self.roles = await guild.get_all_roles()
        return interactions.search_iterable(self.roles, name=role_name)
