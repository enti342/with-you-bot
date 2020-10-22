import discord
import mysql.connector
import os
import withyoubot.footer as footer
import withyoubot.start as start

print("Starting...")

start.start()

TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN = int(os.getenv('ADMIN_ID'))
client = discord.Client()


@client.event
async def on_ready():
    activity = discord.Activity(name="\"with you\"s, sadly", type=discord.ActivityType.listening)
    await client.change_presence(activity=activity)
    print("Bot is ready!")


@client.event
async def on_message(message):
    channel = message.channel
    database = mysql.connector.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_DATABASE")
    )
    # .withyou
    if message.content.lower() == ".withyou":
        # Read the file, add one, read again
        with open('./counter.txt', 'r') as file:
            counter = file.read()
        with open('./counter.txt', 'w') as file:
            file.write(str(int(counter) + 1))
        with open('./counter.txt', 'r') as file:
            counter = file.read()

        write_database = database.cursor(buffered=True)
        write_database.execute("SELECT * FROM withyou WHERE discord_id = " + str(message.author.id))
        exists = write_database.fetchone()

        if exists:
            write_database.execute(
                "UPDATE withyou SET withyou = withyou + 1 WHERE discord_id = " + str(message.author.id))
        else:
            write_database.execute(
                "INSERT INTO withyou (discord_id, withyou, killme) VALUES (" + str(message.author.id) + ", 1, 0)")

        database.commit()

        # We've got our magical number, send the message!
        embed = discord.Embed(title="\"With You\" Bot",
                              type="Rich", description="The \"with you\":tm: counter is now at " + str(counter) + ".",
                              color=0x013162)
        embed.set_footer(text=footer.footer("This \"with you\" was submitted at "))
        await channel.send(embed=embed)

    if message.content.lower() == ".withyou rm":
        # Read the file, remove one, read again
        with open('./counter.txt', 'r') as file:
            counter = file.read()
        with open('./counter.txt', 'w') as file:
            file.write(str(int(counter) - 1))
        with open('./counter.txt', 'r') as file:
            counter = file.read()

        write_database = database.cursor(buffered=True)
        write_database.execute("UPDATE withyou SET withyou = withyou - 1 WHERE discord_id = " + str(message.author.id))
        database.commit()

        # We've got our magical number, send the message!
        embed = discord.Embed(title="\"With You\" Bot", type="Rich",
                              description="A \"with you\" has been removed. The \"with you\":tm: counter is now at " +
                                          str(counter) + ".", color=0x013162)
        embed.set_footer(text=footer.footer("This \"with you\" was removed at "))
        await channel.send(embed=embed)

    if message.content.lower() == ".withyou show":
        # Read the file
        with open('./counter.txt', 'r') as file:
            counter = file.read()

        read_database = database.cursor()
        read_database.execute("SELECT * FROM withyou ORDER BY withyou DESC")
        results = read_database.fetchall()

        final = []
        for x in results:
            if int(x[2]) > 0:
                final.append([x[1], x[2]])

        # Tell them the number that they want to know!
        embed = discord.Embed(title="\"With You\" Bot", type="Rich",
                              description="The \"with you\":tm: counter is at " + str(counter) + ".", color=0x013162)
        for x in final:
            embed.add_field(name="\u200b", value="<@" + str(x[0]) + "> | " + str(x[1]) + " times", inline=True)
        embed.set_footer(text=footer.footer("The \"with you\" counter was viewed at "))
        await channel.send(embed=embed)

    if message.content.lower() == ".withyou help":
        embed = discord.Embed(title="\"With You\" Bot",
                              description="The \"with you\":tm: bot is for \"with you\" check in's by pilots on "
                                          "frequency. Feel free to add one to the counter if you hear one!",
                              color=0x013162)
        embed.add_field(name=".withyou", value="Adds 1 \"with you\" to the counter!", inline=False)
        embed.add_field(name=".withyou rm", value="Removes 1 \"with you\" from the counter!", inline=False)
        embed.add_field(name=".withyou show", value="Lets you see the amount of \"with you\"s in the counter!",
                        inline=False)
        embed.add_field(name=".withyou help", value="This one is fairly easy. It shows you the commands for this bot!",
                        inline=False)
        embed.add_field(name="\u200b",
                        value="Introducing .killme! Made for the times you just want to die while controlling!",
                        inline=False)
        embed.add_field(name=".killme", value="Adds 1 .killme to the counter!", inline=False)
        embed.add_field(name=".killme show",
                        value="Displays the amount of times our controllers have been over-stressed by VATSIM's pilots.",
                        inline=False)
        embed.set_footer(text=footer.footer("The \"with you\" and .killme commands were viewed at"))
        await channel.send(embed=embed)

    if message.content.lower().startswith(".withyou num "):
        # Check if it's me sending the message
        if message.author.id != ADMIN:
            return
        else:
            user = client.get_user(ADMIN)
            new_number = message.content[13:]
            try:
                int(new_number)
                pass
            except ValueError:
                embed = discord.Embed(title="\"With You\" Bot", type="Rich",
                                      description="Uh oh. The number needs to be an integer.", color=0xFF0000)
                embed.set_footer(text=footer.footer("The \"with you\" counter was supposed to be set at "))
                await user.send(embed=embed)
                return

            # Overwrite the current number with the specified
            with open('./counter.txt', 'w') as file:
                file.write(new_number)
            with open('./counter.txt', 'r') as file:
                counter = file.read()

            # Tell me so I know it works!
            embed = discord.Embed(title="\"With You\" Bot", type="Rich",
                                  description="The \"with you\":tm: counter has been set at " + str(counter) + ".",
                                  color=0x013162)
            embed.set_footer(text=footer.footer("The \"with you\" counter was set at "))
            await user.send(embed=embed)

    # .killme
    if message.content.lower() == ".killme":
        # Read the file, add one, read again
        with open('./killme.txt', 'r') as file:
            killme = file.read()
        with open('./killme.txt', 'w') as file:
            file.write(str(int(killme) + 1))
        with open('./killme.txt', 'r') as file:
            killme = file.read()

        write_database = database.cursor(buffered=True)
        write_database.execute("SELECT * FROM withyou WHERE discord_id = " + str(message.author.id))
        exists = write_database.fetchone()

        if exists:
            write_database.execute(
                "UPDATE withyou SET killme = killme + 1 WHERE discord_id = " + str(message.author.id))
        else:
            write_database.execute(
                "INSERT INTO withyou (discord_id, withyou, killme) VALUES (" + str(message.author.id) + ", 0, 1)")

        database.commit()

        # We've got our magical number, send the message!
        embed = discord.Embed(title="\"With You\" Bot", type="Rich",
                              description="There's another `.killme`. The Winnipeg controllers have been over-stressed "
                                          + str(killme) + " times.", color=0x013162)
        embed.set_footer(text=footer.footer("This .killme was submitted at "))
        await channel.send(embed=embed)

    if message.content.lower() == ".killme rm":
        # Read the file, remove one, read again
        with open('./killme.txt', 'r') as file:
            counter = file.read()
        with open('./killme.txt', 'w') as file:
            file.write(str(int(counter) - 1))
        with open('./killme.txt', 'r') as file:
            counter = file.read()

        write_database = database.cursor(buffered=True)
        write_database.execute("UPDATE withyou SET killme = killme - 1 WHERE discord_id = " + str(message.author.id))
        database.commit()

        # We've got our magical number, send the message!
        embed = discord.Embed(title="\"With You\" Bot", type="Rich",
                              description="A kill me has been removed. The 'kill me' counter is now at " + str(
                                  counter) + ".", color=0x013162)
        embed.set_footer(text=footer.footer("This .killme was removed at "))
        await channel.send(embed=embed)

    if message.content.lower() == ".killme show":
        # Read the file
        with open('./killme.txt', 'r') as file:
            killme = file.read()

        read_database = database.cursor()
        read_database.execute("SELECT * FROM withyou ORDER BY killme DESC")
        results = read_database.fetchall()

        final = []
        for x in results:
            if int(x[3]) > 0:
                final.append([x[1], x[3]])

        # Tell them the number that they want to know!
        embed = discord.Embed(title="\"With You\" Bot", type="Rich",
                              description="The Winnipeg controllers have been over-stressed " + str(killme) + " times.",
                              color=0x013162)
        for x in final:
            embed.add_field(name="\u200b", value="<@" + str(x[0]) + "> | " + str(x[1]) + " times", inline=True)
        embed.set_footer(text=footer.footer("The .killme counter was viewed at "))
        await channel.send(embed=embed)


client.run(TOKEN)
