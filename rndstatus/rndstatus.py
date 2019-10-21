from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from random import choice as rndchoice
import os
import time

BaseCog = getattr(commands, "Cog", object)

class RandomStatus(BaseCog):
    """Cycles random statuses

    If a custom status is already set, it won't change it until
    it's back to none. (!set status)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=4530825458)
        self.statuses = self.config.statuses()
        self.last_change = None
        default_global = {
            "statuses": [],
            "settings": {
            "DELAY": 20
            }
        }
        default_guild = {}
        
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
    @commands.group(pass_context=True)
    @checks.is_owner()
    async def rndstatus(self, ctx):
        pass

    @rndstatus.command(name="set", pass_context=True, no_pm=True)
    async def _set(self, ctx, *statuses : str):
        """Sets Red's random statuses

        Accepts multiple statuses.
        Must be enclosed in double quotes in case of multiple words.
        Example:
        !rndstatus set \"Tomb Raider II\" \"Transistor\" \"with your heart.\"
        Shows current list if empty."""
        current_status = ctx.message.guild.me.status
        if statuses == () or "" in statuses:
            await ctx.author.send("Current statuses: " + " | ".join(self.statuses))
            return
        stat = list(statuses)
        await self.config.statuses.set(stat)
        await self.bot.change_presence(status=current_status)
        await ctx.send("Done. Redo this command with no parameters to see the current list of statuses.")


    @rndstatus.command(pass_context=True)
    async def delay(self, ctx, seconds : int):
        """Sets interval of random status switch

        Must be 20 or superior."""
        if seconds < 20:
            return
        await self.config.settings.DELAY.set(seconds)
        await ctx.send("Interval set to {}".format(str(seconds)))

    async def switch_status(self, message):
        if not message.channel.is_private:
            current_game = str(message.server.me.game)
            current_status = message.server.me.status

            if self.last_change == None: #first run
                self.last_change = int(time.perf_counter())
                if len(self.statuses) > 0 and (current_game in self.statuses or current_game == "None"):
                    new_game = self.random_status(message)
                    await self.bot.change_presence(game=discord.Game(name=new_game), status=current_status)

            if message.author.id != self.bot.user.id:
                if abs(self.last_change - int(time.perf_counter())) >= self.settings["DELAY"]:
                    self.last_change = int(time.perf_counter())
                    new_game = self.random_status(message)
                    if new_game != None:
                        if current_game != new_game:
                            if current_game in self.statuses or current_game == "None": #Prevents rndstatus from overwriting song's titles or
                                await self.bot.change_presence(game=discord.Game(name=new_game), status=current_status) #custom statuses set with !set status

    def random_status(self, msg):
        current = str(msg.server.me.game)
        new = str(msg.server.me.game)
        if len(self.statuses) > 1:
            while current == new:
                new = rndchoice(self.statuses)
        elif len(self.statuses) == 1:
            new = self.statuses[0]
        else:
            new = None
        return new
