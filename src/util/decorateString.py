from typing import Callable, List, Optional

import interactions


class StringBlock:
    def __init__(self, initial_message=""):
        self._msg = initial_message
        self._transform: List[Callable[[str], str]] = []

    def add_transform(self, lam):
        self._transform.append(lam)
        return self

    def surround_default_codeBlock(self, lang=""):
        self._transform.append(lambda x: f"```{lang}\n{x}\n```")
        return self

    def add_text(self, text):
        self._msg += text
        return self

    def dump(self) -> str:
        ret_msg: str = self._msg
        for trans in self._transform:
            ret_msg = trans(ret_msg)
        return ret_msg


class MutableMessage(StringBlock):
    def __init__(self, ctx: interactions.CommandContext, initial_message="", existing_msg=None):
        super().__init__(initial_message=initial_message)
        self.ctx = ctx
        self.ctxMsg: Optional[interactions.Message] = existing_msg

    async def send(self):
        if not self.ctxMsg:
            self.ctxMsg = await self.ctx.send(self.dump())
        else:
            await self.ctxMsg.edit(self.dump())




