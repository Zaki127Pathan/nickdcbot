from keep_alive import keep_alive
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

def get_prefix(bot, message):
    return ["=", "-"]

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
invite_tracker = {}

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name}")
    for guild in bot.guilds:
        try:
            invite_tracker[guild.id] = await guild.invites()
        except discord.Forbidden:
            pass

class TicketButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, emoji="🎫", custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{member.name}", 
            overwrites=overwrites, 
            topic=f"Ticket for {member.id}"
        )
        
        await interaction.response.send_message(f"Your ticket has been created at {ticket_channel.mention}!", ephemeral=True)
        
        ticket_embed = discord.Embed(
            title="Ticket Support Panel",
            description=f"Welcome {member.mention} to your private support channel!\n\nOur staff team has been notified. Please list your issues or questions below.",
            color=discord.Color.blue()
        )
        ticket_embed.add_field(name="Ticket Creator", value=member.mention, inline=True)
        ticket_embed.add_field(name="Status", value="📌 Awaiting Staff", inline=True)
        ticket_embed.set_footer(text="Type -close to shut down this ticket panel completely.")
        
        await ticket_channel.send(embed=ticket_embed)

@bot.command(name="setup-ticket")
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    view = TicketButtonView()
    
    panel_embed = discord.Embed(
        title="🎫 Server Support Tickets",
        description="Need help, want to report a user, or have a question for the administration team?\n\nClick the button below to open a private conversation window with our server staff.",
        color=discord.Color.green()
    )
    if bot.user.avatar:
        panel_embed.set_thumbnail(url=bot.user.avatar.url)
    panel_embed.add_field(name="⏰ Response Expectations", value="A staff member will be with you shortly.", inline=False)
    panel_embed.set_footer(text="Please do not spam ticket creation threads.")
    
    await ctx.send(embed=panel_embed, view=view)

@bot.command(name="close")
async def close_ticket(ctx):
    if ctx.channel.name.startswith("ticket-"):
        await ctx.send("Closing channel in 5 seconds...")
        await ctx.channel.delete()
    else:
        await ctx.send("This command can only be used inside an active ticket channel.")

@bot.command(name="i")
async def check_invites(ctx):
    try:
        current_invites = await ctx.guild.invites()
    except discord.Forbidden:
        await ctx.send("I do not have permission to check invites.")
        return
    author_invites = [inv for inv in current_invites if inv.inviter == ctx.author]
    total_uses = sum(inv.uses for inv in author_invites)
    await ctx.send(f"{ctx.author.mention}, you have generated **{len(author_invites)}** invite links with **{total_uses}** uses.")

@bot.command(name="members")
async def member_count(ctx):
    await ctx.send(f"Total members in this server: **{ctx.guild.member_count}**")

@bot.command(name="giverole")
@commands.has_permissions(manage_roles=True)
async def give_default_role(ctx, member: discord.Member, role: discord.Role):
    if len(member.roles) == 1:
        try:
            await member.add_roles(role)
            await ctx.send(f"Successfully added {role.mention} to {member.mention}.")
        except discord.Forbidden:
            await ctx.send("I cannot add that role. Check my role hierarchy position.")
    else:
        await ctx.send(f"{member.mention} already has other roles assigned.")

@bot.event
async def setup_hook():
    bot.add_view(TicketButtonView())

keep_alive()
bot.run("MTU2NzU4MjQzMjEwNDgxNjY4MA.GffnZ2.aYG85RJ2c1PAw5tj64KF7PyYQwHPdXCUWTCsio")
