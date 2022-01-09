import discord
from discord import Embed
from discord.ext import commands
from discord.ui import View, Button, Select
from discord.utils import get

token = <your token goes here>
server_id = <the id of the server goes here>
server_name = <the name of the server goes here>
prefix = '!'

verification_channel_id = 929675551042576384
welcome_role_id = 929680255604629515
rules = {"these": "are", "some": "test", "rules": "we'll", }
channel_rules = {"gen": "need", "mod_ping": "new", "rules": "ones"}

roles_channel_id = 929675957755867157
roles = {929680592382091276: ("Semi-Pro",
                              "I make some money with my photography but do not consider it my main source of income."),
         929680544667676672: ("Advanced",
                              "I can correctly expose for different lighting conditions using manual settings."),
         929680509448101968: ("Novice", "I can use my camera, generally on automatic settings."),
         929680455442268171: ("Brand New", "I just got my camera and need to learn the basics."),
         929680324168921130: ("More Money than Sense",
                              "I have no idea how to use my gear but I still brought top of the line equipment new because I can afford it.")
         }

verifiable_roles = {929680628876726274: (
    "Professional", "I make the majority (if not all) of my income from my photography")}
mod_ping_channel_id = 929675432486379550

brands_channel_id = 123
brands = 1234

COLOUR = discord.Color.fuchsia()


class ButtonVerify(Button):
    # a variation of the Button class allowing for one-click verification.
    def __init__(self, bot, welcome_role, server, welcome_message):
        self.bot = bot
        self.welcome_role = welcome_role
        self.server_id = server
        self.welcome_message = welcome_message
        super(ButtonVerify, self).__init__(style=discord.ButtonStyle.green,
                                           label='Click to verify!')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild = await self.bot.fetch_guild(self.server_id)
        user_object = interaction.user
        role_object = get(guild.roles, id=self.welcome_role)
        await interaction.followup.send(content=None,
                                        embed=Embed(
                                            title='You\'ve been verified!',
                                            description=self.welcome_message,
                                            colour=COLOUR),
                                        ephemeral=True)
        await user_object.add_roles(role_object)


class RoleSelect(Select):
    # subclass of 'select', allowing for role manipulation
    def __init__(self, bot, roles, verifiable_roles, mod_ping_channel, server, server_id, welcome_role,
                 placeholder):
        self.bot = bot
        self.user_roles = roles
        self.verifiable_user_roles = verifiable_roles
        self.verify_notification_target = mod_ping_channel
        self.server = server
        self.server_id = server_id
        self.welcome_role = welcome_role
        super(RoleSelect, self).__init__(placeholder=placeholder)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role = int(interaction.data['values'][0])
        guild = interaction.guild
        welcome_role_item = guild.get_role(self.welcome_role)
        await interaction.response.defer()
        guild_roles = await guild.fetch_roles()

        role_item = list(guild_roles)[[role.id for role in guild_roles].index(role)]

        role_name = role_item.name

        if role not in user.roles:
            if welcome_role_item in user.roles or len(set(user.roles).intersection(
                                                      set(guild.get_role(role_id) for role_id in
                                                          list(self.user_roles.keys())+
                                                          list(self.verifiable_user_roles.keys())
                                                          ))) > 0:
                if role in self.verifiable_user_roles.keys():
                    # message role_moderator
                    mod_notification_channel = guild.get_channel(self.verify_notification_target)

                    await mod_notification_channel.send(
                        embed=Embed(
                            title=f"User '{user.name}' in {self.server} has requested the role "
                                  f"'{role_name}' which requires moderator verification.",
                            description='',
                            colour=COLOUR))

                    await interaction.followup.send(content=None,
                                                    embed=Embed(
                                                        title=f'Role Chosen: {role_name}',
                                                        description='A moderator will '
                                                                    'review your '
                                                                    'application and '
                                                                    'respond soon.',
                                                        colour=COLOUR),
                                                    ephemeral=True)

                elif role in self.user_roles.keys():
                    roles_managed = set()
                    for key in self.verifiable_user_roles.keys():
                        roles_managed.add(get(guild.roles, id=key))

                    for key in self.user_roles.keys():
                        roles_managed.add(get(guild.roles, id=key))

                    roles_managed.add(get(guild.roles, id=self.welcome_role))

                    for role in roles_managed:
                        await user.remove_roles(role)

                    # grant the new role role_item
                    await user.add_roles(role_item)

                    await interaction.followup.send(content=None,
                                                    embed=Embed(
                                                        title=f'Role Chosen: {role_name}',
                                                        description='The role has been '
                                                                    'granted.',
                                                        colour=COLOUR),
                                                    ephemeral=True)
            else:
                print("user hasn't got the role")
                await interaction.followup.send(content=None,
                                                embed=Embed(
                                                    title="Verification Error",
                                                    description="You are not yet verified. "
                                                                "Please do so first.",
                                                    colour=COLOUR),
                                                ephemeral=True)


def verification(bot, welcome_role_id, server_id, welcome_message, rules, channel_rules):
    embed_list = []
    embed_one = Embed(title='Rules',
                      description='Use the green button below to verify yourself when you '
                                  'have read and understood the rules.',
                      colour=COLOUR,
                      )
    embed_one.set_footer(text=("\u3000" * 300))

    for rule in rules.keys():
        embed_one.add_field(name=rule,
                            value=rules[rule] + '\n' if len(rules[rule])
                                                        > 2 else '\u200b\n',
                            inline=False)
    if len(rules.keys()) >= 1:
        embed_list.append(embed_one)

    embed_two = Embed(title='Channel Specific Rules and Guidelines',
                      description='\u3000',
                      colour=COLOUR
                      )
    embed_two.set_footer(text=("\u3000" * 300))

    for rule in channel_rules.keys():
        embed_two.add_field(name=rule,
                            value=channel_rules[rule] + '\n' if len(channel_rules[rule])
                                                                > 2 else '\u200b\n',
                            inline=False)
    if len(channel_rules.keys()) >= 1:
        embed_list.append(embed_two)

    verify_button = ButtonVerify(bot, welcome_role_id, server_id, welcome_message)
    view = View(verify_button, timeout=None)
    return view, embed_list


def role_select(bot, user_roles, verifiable_user_roles, mod_channel, server_name, server_id,
                welcome_role_id):
    embed_description_string = "Use the drop-down to select a role, " \
                               "appropriate to your photography experience."

    embed = discord.Embed(title='Set Your Role',
                          description=embed_description_string,
                          color=COLOUR
                          )
    embed.set_footer(text=("\u3000" * 300))

    for item in verifiable_user_roles.keys():
        embed.add_field(name=verifiable_user_roles[item][0],
                        value=' - ' + verifiable_user_roles[item][1] +
                              '\n- **This role requires verification by a moderator.**',
                        inline=False)

    for item in user_roles.keys():
        embed.add_field(name=user_roles[item][0],
                        value=' - ' + user_roles[item][1],
                        inline=False)

    role_select = RoleSelect(bot=bot, roles=user_roles, verifiable_roles=verifiable_user_roles,
                             mod_ping_channel=mod_channel,
                             server=server_name, server_id=server_id,
                             welcome_role=welcome_role_id,
                             placeholder='Pick a Role!'
                             )

    for item in verifiable_user_roles.keys():
        role_select.add_option(label=verifiable_user_roles[item][0],
                               value=item,
                               description='requires moderator approval.'
                               )

    for item in user_roles.keys():
        role_select.add_option(label=user_roles[item][0],
                               value=item,
                               description=''
                               )

    return View(role_select, timeout=None), embed


robot = commands.Bot(command_prefix=prefix,
                     case_insensitive=True)


@robot.event
async def on_ready():
    print("dis kommand verks")
    verification_channel = robot.get_channel(int(verification_channel_id))
    async for message in verification_channel.history(limit=200):
        if message.author == robot.user:
            await message.delete()

    roles_channel = robot.get_channel(int(roles_channel_id))
    async for message in roles_channel.history(limit=200):
        if message.author == robot.user:
            await message.delete()

    verification_view, verification_embeds = verification(bot=robot,
                                                          welcome_role_id=welcome_role_id,
                                                          server_id=server_id,
                                                          welcome_message="this is a generic welcome message",
                                                          rules=rules,
                                                          channel_rules=channel_rules
                                                          )

    experience_roles_view, experience_roles_embed = role_select(bot=robot,
                                                                user_roles=roles,
                                                                verifiable_user_roles=verifiable_roles,
                                                                mod_channel=mod_ping_channel_id,
                                                                server_name=server_name,
                                                                server_id=server_id,
                                                                welcome_role_id=welcome_role_id)

    print(verification_embeds, verification_view)
    await verification_channel.send(embeds=verification_embeds, view=verification_view)
    print(experience_roles_embed, experience_roles_view)
    await roles_channel.send(embed=experience_roles_embed, view=experience_roles_view)


@robot.command()
async def dprint(ctx):
    print("yer mum gae")


robot.run(token)
