import sys
try: import discord
except ImportError: sys.exit("discord module is required, try 'pip3 install discord.py'")
try: from settings import *
except ImportError: sys.exit("Error importing settings")
except SyntaxError: sys.exit("Error importing settings, check syntax of settings.py")

class BotClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.run(TOKEN)

    @staticmethod
    def unwrap_payload(payload): return (payload.message_id, payload.user_id, payload.emoji.name)

    async def on_raw_reaction_add(self, p) -> None: await self.change_role(self.unwrap_payload(p), True)

    async def on_raw_reaction_remove(self, p) -> None: await self.change_role(self.unwrap_payload(p), False)

    async def has_role(self, user_obj, role_obj) -> bool: return role_obj.id in [x.id for x in user_obj.roles]

    async def on_ready(self) -> None:
        print(f'Ready, logged in as {self.user} on {self.guilds[0].name}\n---')
        await self.check_reactions()

    async def change_role(self, payload, add_rem) -> None:
        if payload[0] == REACTION_MESSAGE_ID:
            try: role_name = REACTION_MATCH[payload[2]]
            except KeyError: return

            if role_name in [x.name for x in self.guilds[0].roles]:
                role_obj = discord.utils.get(self.guilds[0].roles, name=role_name)
                user_obj = discord.utils.find(lambda m: m.id == payload[1], self.guilds[0].members)

                if user_obj and role_obj:
                    if add_rem is True and not await self.has_role(user_obj, role_obj):
                        await user_obj.add_roles(role_obj)
                        print(f"[+] {user_obj.name}\tassigned\t{role_obj.name}")
                    elif add_rem is False and await self.has_role(user_obj, role_obj):
                        await user_obj.remove_roles(role_obj)
                        print(f"[-] {user_obj.name}\tunassigned\t{role_obj.name}")
                    else: return
                else: return
            else: return
        else: return

    async def check_reactions(self) -> None:
        channel = self.guilds[0].get_channel(REACTION_CHANNEL_ID)
        if channel == None: sys.exit("Channel could not be found, check settings.py")

        try: message = await channel.fetch_message(REACTION_MESSAGE_ID)
        except discord.errors.NotFound: sys.exit("Message with reactions not found, check settings.py")
        except discord.errors.Forbidden: sys.exit("Bot needs permission to read message history")
        except discord.errors.HTTPException: sys.exit("Reading reaction message failed")

        for reaction in message.reactions:
            emoji = reaction.emoji

            async for user in reaction.users():
                if not isinstance(emoji, str): emoji = emoji.name
                await self.change_role((REACTION_MESSAGE_ID, user.id, emoji), True)

if __name__ == "__main__": BotClient()
else: sys.exit("This script should not be run as a module")
