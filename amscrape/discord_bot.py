import os
import discord
import asyncio
from am.secret import DISCORD_TOKEN


intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)


async def on_ready(user_id, message):
    user = await client.fetch_user(int(user_id))
    if user:
        message_content = f'{user.mention} {message}'
        await user.send(message_content)
    await client.close()


def send_warning(user_id, message):
    async def run_on_ready():
        await client.wait_until_ready()
        await on_ready(user_id, message)
        await client.close()

    loop = asyncio.new_event_loop()
    loop.create_task(client.start(DISCORD_TOKEN))
    loop.run_until_complete(run_on_ready())
