import discord
import os
import hashlib
from discord import Message
from discord.errors import Forbidden, HTTPException, NotFound
from spawningtool.exception import ReadError, ReplayFormatError
import spawningtool.parser
import utils
import constants as const
import io

class BOGClient(discord.Client):
    """ Represents the Discord Bot Client """

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

                f = io.StringIO(total)
                result = discord.File(f, filename='buildorder.txt')
                await message.reply(file=result)

            except (HTTPException, NotFound, Forbidden) as e: # standard discord errors
                await message.reply('Unable to access replay')
            except (ReadError, ReplayFormatError) as e: # parse errors spawning tool
                await message.reply('This does not look like a replay')
            except: # needed if we get an unparsable replay
                await message.reply('Unable to parse replay')
