import sys
import asyncio

try: import discord, discord.ext.tasks as tasks
except ImportError: sys.exit("discord module is required, try 'pip3 install discord.py'")

try: from settings import *
except ImportError: sys.exit("Error importing settings")
except SyntaxError: sys.exit("Error importing settings, check syntax of settings.py")

class BotClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.run(TOKEN)

    async def on_raw_reaction_add(self, p) -> None: await self.grant_role(self.unwrap_payload(p))
    async def on_raw_reaction_remove(self, p) -> None: await self.remove_role(self.unwrap_payload(p))
    async def has_role(self, user_obj, role_obj) -> bool: return role_obj.id in [x.id for x in user_obj.roles]

    @staticmethod
    def unwrap_payload(payload) -> tuple: return (payload.message_id, payload.user_id, payload.emoji.name)

    @staticmethod
    def match_role(emoji):
        try: return REACTION_MATCH[emoji]
        except KeyError: return None

    async def on_ready(self) -> None:
        print(f'Ready, logged in as {self.user} on {self.guilds[0].name}\n---')
        await self.check_reactions()

        # Testing async tasks
        @tasks.loop(seconds=10.0)
        async def do_if_role_present(): pass
        await do_if_role_present.start()
        # End

    async def grant_role(self, payload) -> None:
        if payload[0] == REACTION_MESSAGE_ID: role_name = self.match_role(payload[2])

        if role_name is not None and role_name in [x.name for x in self.guilds[0].roles]:
            role_obj = discord.utils.get(self.guilds[0].roles, name=role_name)
            user_obj = discord.utils.find(lambda m: m.id == payload[1], self.guilds[0].members)

            if user_obj and role_obj and role_obj.id not in [x.id for x in user_obj.roles]:
                await user_obj.add_roles(role_obj)
                print(f"[+] {user_obj.name}\tassigned\t{role_obj.name}")
            else: return
        else: return

    async def remove_role(self, payload) -> None:
        if payload[0] == REACTION_MESSAGE_ID: role_name = self.match_role(payload[2])

        if role_name is not None and role_name in [x.name for x in self.guilds[0].roles]:
            role_obj = discord.utils.get(self.guilds[0].roles, name=role_name)
            user_obj = discord.utils.find(lambda m: m.id == payload[1], self.guilds[0].members)

            if user_obj and role_obj and role_obj.id in [x.id for x in user_obj.roles]:
                await user_obj.remove_roles(role_obj)
                print(f"[-] {user_obj.name}\tunassigned\t{role_obj.name}")
            else: return
        else: return

    async def check_reactions(self) -> None:
        checked_users = set()

        channel = self.guilds[0].get_channel(REACTION_CHANNEL_ID)
        if channel == None: sys.exit("Channel could not be found, check settings.py")

        try: message = await channel.fetch_message(REACTION_MESSAGE_ID)
        except discord.errors.NotFound: sys.exit("Message with reactions not found, check settings.py")
        except discord.errors.Forbidden: sys.exit("Bot needs permission to read message history")
        except discord.errors.HTTPException: sys.exit("Reading reaction message failed")

        for reaction in message.reactions:
            emoji = reaction.emoji if isinstance(reaction.emoji, str) else reaction.emoji.name
            async for user in reaction.users():
                await self.grant_role((REACTION_MESSAGE_ID, user.id, emoji))
                checked_users.add(user)

        to_check = set(self.guilds[0].members).difference(checked_users)

        for user in to_check:
            for match in REACTION_MATCH: await self.remove_role((REACTION_MESSAGE_ID, user.id, match))

if __name__ == "__main__": BotClient()
else: sys.exit("This script should not be run as a module")
