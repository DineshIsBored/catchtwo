import discum, re, time, multiprocessing, json, datetime

version = "v2.4.1"

with open("data/config.json", "r") as file:
    info = json.loads(file.read())
    user_token = info["user_token"]
    channel_id = info["channel_id"]

with open("data/pokemon", "r",encoding="utf8") as file:
    _pokemon = file.read()
with open("data/legendary", "r") as file:
    _legendart = file.read()
with open("data/mythical", "r") as file:
    _mythical = file.read()
    
poketwo_id = 716390085896962058

pokemon = 0
shiny = 0
legendary = 0
mythical = 0
fled = 0

bot = discum.Client(token=user_token, log=False)

def solve(message):
    hint = []
    for i in range(15,len(message) - 1):
        if message[i] != "\\":
            hint.append(message[i])
    hint_string = ""
    for i in hint:
        hint_string += i
    hint_replaced = hint_string.replace("_", ".")
    solution = re.findall('^'+hint_replaced+'$', _pokemon, re.MULTILINE)
    return solution

def spam():
    while True:
        bot.sendMessage(channel_id, "A")
        time.sleep(2)

def start_spam_process():
    new_process = multiprocessing.Process(target=spam)
    new_process.start()
    return new_process

def stop_process(process_to_stop):
    process_to_stop.terminate()

def print_log(string):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("-", current_time, "- ", string)

@bot.gateway.command
def on_ready(resp):
    if resp.event.ready_supplemental:
        user = bot.gateway.session.user
        print_log(f"Logged in as: {user['username']}#{user['discriminator']}")

@bot.gateway.command
def on_message(resp):
    global spam_process
    if resp.event.message:
        m = resp.parsed.auto()
        if m["channel_id"] == channel_id: # If a message is in the right channel
            if m["author"]["id"] == poketwo_id: # If it's a message sent by Poketwo
                if m["embeds"]: # If the message contains an embed
                    embed_title = m["embeds"][0]["title"]
                
                    if "A wild pokémon has appeared!" in embed_title: # If a wild pokemon appears
                        stop_process(spam_process)
                        time.sleep(2)
                        bot.sendMessage(channel_id, "p!h")

                    elif "A new wild pokémon has appeared!" in embed_title: # If new wild pokemon appeared after one fled.
                        global fled
                        fled += 1
                        print_log("A pokemon has fled.")

                        time.sleep(2)
                        bot.sendMessage(channel_id, "p!h")

                else: # If the message is not an embedded message
                    content = m["content"]
                    if "The pokémon is " in content: # If the message is a hint
                        solution = solve(content)
                        if len(solution) == 0:
                            print_log("Pokemon could not be found in the database.")
                            for i in range(0,len(solution)):
                                time.sleep(2)
                                bot.sendMessage(channel_id, "p!c " + solution[i])
                        spam_process = start_spam_process()

                    elif "Congratulations" in content: # If a pokemon is caught
                        global pokemon
                        pokemon += 1
                        if "These colors seem unusual..." in content: # If the pokemon caught is shiny
                            global shiny
                            shiny += 1
                        split = content.split(" ")
                        msg = ""
                        for i in range (2,len(split)):
                            msg += split[i] + " "
                        print_log(msg)
                        pokemon = split[7].replace("!", "")
                        if re.findall('^'+pokemon+'$',_legendart,re.MULTILINE): # If pokemon caught is legendary
                            global legendary
                            legendary += 1
                        if re.findall('^'+pokemon+'$',_mythical,re.MULTILINE): # If pokemon caught is mythical
                            global mythical
                            mythical += 1

                    elif "Whoa there. Please tell us you're human!" in content: # If a captcha appears
                        stop_process(spam_process)
                        print_log("Captcha detected, program paused. Press enter to restart.")
                        input()
                        bot.sendMessage(channel_id, "p!h")

if __name__ == "__main__":
    print(f"Pokétwo Autocatcher {version}")
    print("A truly open-source and free Pokétwo autocatcher.")
    print("\nEvent Log:")

    spam_process = start_spam_process()
    bot.gateway.run(auto_reconnect=True)