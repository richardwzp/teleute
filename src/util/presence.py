import datetime
import json

import interactions

from Config import get_path_from_src
from src.databasectl.postgres import PostgresQLDatabase

with open(get_path_from_src(['util', 'presence.json']), 'r') as f:
    presence = json.loads(f.read())

weekday_table = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
}


class PresenceManager:
    def __init__(self, client: interactions.Client, db: PostgresQLDatabase):
        self.bot = client
        self.db = db
        self.presence = presence

    def get_weekday(self):
        return weekday_table[datetime.datetime.today().weekday()]

    async def change_presence(self):
        weekday = self.get_weekday()
        new_presence = presence[weekday]
        print(f'updating presence to be: {new_presence}')
        await self.bot.change_presence(
            interactions.ClientPresence(
                activities=[
                    interactions.PresenceActivity(
                        name=new_presence,
                        details=new_presence,
                        type=interactions.PresenceActivityType.GAME)])
        )