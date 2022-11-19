import discord
import os
import hashlib
from discord import Message, Intents
from discord.errors import Forbidden, HTTPException, NotFound
from spawningtool.exception import ReadError, ReplayFormatError
import spawningtool.parser
import utils
import constants as const
import io

class BOGClient(discord.Client):
    """ Represents the Discord Bot Client """
    def __init__(self):
        super().__init__(intents=Intents(message_content=True, messages=True))


    async def on_ready(self):
        print("BOG is now running.")
        return


    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if not message.attachments:
            return

        for attachment in filter(utils.is_replay, message.attachments):
            try:
                msg = message.content
                replaydata = await attachment.read()
                replayhash = hashlib.md5(replaydata).hexdigest()
                os.makedirs(const.UPLOAD_DIR, exist_ok=True)

                basename = replayhash + const.SC2EXT
                filepath = os.path.join(const.UPLOAD_DIR, basename)

                f = open(filepath, 'wb')
                f.write(replaydata)
                f.close()
                replay = spawningtool.parser.parse_replay(filepath, cache_dir=const.CACHEDIR)
                total = utils.get_replay_strs(replay, msg)
                replay_str_output = io.BytesIO(bytes(total, 'utf-8'))

                result = discord.File(replay_str_output, filename='buildorder.txt')
                await message.reply(file=result)

            except (HTTPException, NotFound, Forbidden) as _: # standard discord errors
                await message.reply('Unable to access replay')
            except (ReadError, ReplayFormatError) as _: # parse errors spawning tool
                await message.reply('This does not look like a replay')
            except Exception as e: # needed if we get an unparsable replay
                await message.reply('Unable to parse replay.\n```{}```'.format(e))
                # TODO: may want to save the breaking replay for debugging purposes later on.
