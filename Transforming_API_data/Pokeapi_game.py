import time
import requests #requests needs to be installed either using the pycharm interface or by 'pip install requests' on the terminal
import random
import json

def intro():
    '''
    This function asks players if they would like to play, "y" continues the game, "n" closes it.
    :return:
    '''
    print("~~~~ WELCOME TO THE MONSTER BATTLE GAME ~~~~")
    time.sleep(1)
    print("This game uses the JSON data from PokeApi and transforms it into a game")
    time.sleep(2)

    answer = input("\nWould you like to play? (y/n): ")
    time.sleep(1)
    answer = answer.lower()

    if answer == "yes" or answer == "y":
        print("\nWelcome!")
    else:
        print("\nGame Over \n(Please run the programme again!)")
        exit()


def get_monster(monster_nums_list, name="Opponent"):
    '''
    This function retrieves the data for the player's or opponent's monster using the 3 random numbers inputted or generated previously.

    The function creates an empty dictionary variable (monster_dict) ready to capture selected data retrieved
    from the API.  I used three different ways to demonstrate cleaning the data. The first I split and sliced the strings
    returned.  The second I split the stripped the punctuation characters out.  The third is a neater way, I saved the
    json data into a dictionary and then looked up the keys I wanted.

    The for loop obtains the name and type of monster, a nested for loop then retrieves 3 different moves and corresponding
    powers and saves them to first a dictionary (monster_move_dict), and then appends each to a list
     (monster_moves_list).

    These are then all appended to the monster_dict for future use.

    '''

    monster_dict = {}

    # GET request based on monster numbers
    for i, monster_num in enumerate(monster_nums_list):

        monster_data = str(requests.get(f"https://pokeapi.co/api/v2/pokemon-form/{monster_num}/").json())

        # gets and cleans name and type
        monster_name = monster_data.split()
        monster_name = monster_name[15]
        monster_name = monster_name[1:-2]


        monster_type = monster_data.split()
        monster_type = monster_type[47].strip(",:'\"")

        # gets the move
        monster_move_list = []
        monster_move_dict = {}

        monster_base_url = requests.get(f"https://pokeapi.co/api/v2/pokemon/{monster_num}").json()
        monster_base_dict = dict(monster_base_url)

        # saves into variables the move name and url which contains the power
        for move in range(3):

            #this try/except block tries to handle the rare error of a monster not having enough moves.
            try:
                monster_move_name = monster_base_dict["moves"][move]["move"]["name"]

            except IndexError:
                print("I'm so sorry there has been an error retrieving moves :(")
                print("The game will now close, please run again and choose different monster numbers")
                time.sleep(3)
                exit()

            monster_move_url = monster_base_dict["moves"][move]["move"]["url"]

            #fetches the power of the move
            monster_moves_data = requests.get(f"{monster_move_url}").json()
            monster_moves_data_dict = dict(monster_moves_data)

            monster_move_power = monster_moves_data_dict["power"]

            # handles the error if the power returns None
            if monster_move_power is None:
                monster_move_power = 0

            #updates the move dictionary with move and power
            monster_move_dict["move_" + str(move + 1)] = {"move": monster_move_name,
                                                               "power": monster_move_power}

        # Appends the move dictionary to the move list on each loop
        monster_move_list.append(monster_move_dict)

        #creates an empty stats list
        monster_stats_list = []

        # retrieves the stats
        for stat in range(5):
            # saves into variables the stat name and corresponding strength
            monster_stat_name = monster_base_dict["stats"][stat]["stat"]["name"]
            monster_stat_strength = monster_base_dict["stats"][stat]["base_stat"]

            # Each stat and strength is added to a list
            monster_stats_list.append(monster_stat_name)
            monster_stats_list.append(monster_stat_strength)


        # displays to the player which monster they/their opponent chose
        if i == 0:
             print(f"\n{name} chose: ")

        print(f"{monster_name.capitalize()}, who is a {monster_type} type!")

        # monster_dict is then added to on completion of each loop.
        # each monster has its own list of nested dictionaries.
        monster_dict["monster_" + str(i + 1)] = {"name": monster_name,
                                                              "type": monster_type,
                                                              "moves_list": monster_move_list, "stats": monster_stats_list}

    return monster_dict


def get_opponent_monster_nums():
    '''
    This function generates random numbers between 1 and 151 to simulate an opponent picking monster for their team.
    These numbers are then appended to a list that is returned.
    '''
    opponent_monster_numbers_list = []
    for pick in range(3):
        opponent_monster_numbers_list.append((random.randint(1, 151)))

    return opponent_monster_numbers_list


def get_battle_monster(username, chosen_monster_dict, opponent_monster_dict):
    '''
    This function asks the player to select one of their monster to battle.  The player is displayed each of their
    monster and has to provide input of 1, 2 or 3.  A similar process runs for the opponent but a random number is
    generated.
    :param username:
    :param chosen_monster_dict:
    :param opponent_monster_dict:
    :return:
    '''

    #displays to player the battle messages
    print("\n============================================\n||           IT'S TIME TO BATTLE          ||\n============================================")
    time.sleep(2)

    #prints the 3 monster the player has previously chosen
    print(f"\n{username}'s monsters:\n   1. {chosen_monster_dict["monster_1"]["name"].capitalize()}\n   2. {chosen_monster_dict["monster_2"]["name"].capitalize()}\n   3. {chosen_monster_dict["monster_3"]["name"].capitalize()}")

    #asks player to select their chosen battle monster
    chosen_battle_monster = int(input("Which monster do you wish to choose for battle? (1, 2 or 3): "))
    time.sleep(1)

    #this if statement prints out the corresponding monster and saves this choice to a new variable
    if chosen_battle_monster == 1:
        print(f"\n==========>>> GOOOOOOOOO {chosen_monster_dict["monster_1"]["name"].capitalize()}")
        chosen_battle_monster = chosen_monster_dict["monster_1"]

    elif chosen_battle_monster == 2:
        print(f"\n==========>>> GOOOOOOOOO {chosen_monster_dict["monster_2"]["name"].capitalize()}")
        chosen_battle_monster = chosen_monster_dict["monster_2"]

    else:
        print(f"\n==========>>> GOOOOOOOOO {chosen_monster_dict["monster_3"]["name"].capitalize()}")
        chosen_battle_monster = chosen_monster_dict["monster_3"]

    time.sleep(1)

    #a random number is generated to select the opponent's battle monster
    opponent_battle_monster = random.randint(1, 3)

    #the opponent's battle monster is printed out and saved to a variable
    if opponent_battle_monster == 1:
        print(f"          <<<========== Your opponent sent out {opponent_monster_dict["monster_1"]["name"].capitalize()}!")
        opponent_battle_monster = opponent_monster_dict["monster_1"]
    elif opponent_battle_monster == 2:
        print(f"          <<<========== Your opponent sent out {opponent_monster_dict["monster_2"]["name"].capitalize()}!")
        opponent_battle_monster = opponent_monster_dict["monster_2"]
    else:
        print(f"          <<<========== Your opponent sent out {opponent_monster_dict["monster_3"]["name"].capitalize()}!")
        opponent_battle_monster = opponent_monster_dict["monster_3"]

    return chosen_battle_monster, opponent_battle_monster


def get_battle_move(battle_monster, battle_move_num = 0, name="Opponent"):
    '''
    This function takes the selected inputted or generated integer for the battle move and selects the name of it from the dictionary.
    :param opponent_battle_monster:
    :return:
    '''

    #the first if statement triggers when passed the player's details (as only the player needs a printed display of moves)
    if name != "Opponent":
        print(f"\n{battle_monster["name"].capitalize()}'s Moves:\n   1. {battle_monster["moves_list"][0]["move_1"]["move"]}\n   2. {battle_monster["moves_list"][0]["move_2"]["move"]}\n   3. {battle_monster["moves_list"][0]["move_3"]["move"]}")

        # Asks for player input of which move they would like to select
        battle_move_num = int(input(f"Which move should {battle_monster["name"].capitalize()} use? (1, 2 or 3): "))

    else:
        pass

    # saves the selected move into the variable
    if battle_move_num == 1:
        battle_move = battle_monster["moves_list"][0]["move_1"]

    elif battle_move_num == 2:
        battle_move = battle_monster["moves_list"][0]["move_2"]

    else:
        battle_move= battle_monster["moves_list"][0]["move_3"]

    return battle_move


def battle(username, chosen_battle_monster, opponent_battle_monster, chosen_battle_move, opponent_battle_move):
    '''
    This function provides a simple monster battle simulation.  The player's and opponent's monster battle each other and
    the strongest move wins.
    :param username:
    :param chosen_battle_monster:
    :param opponent_battle_monster:
    :param chosen_battle_move:
    :param opponent_battle_move:
    :return:
    '''

    #displays to the player the battle screen, where each monster and selected move is shown
    print(f"\n============================================>>\n                 {chosen_battle_monster["name"].capitalize()} Vs. {opponent_battle_monster["name"].capitalize()}        \n============================================>>")

    print(f"{opponent_battle_monster["name"].upper()} used {opponent_battle_move["move"].upper()}")
    print(f"                     name:|{opponent_battle_monster["name"].capitalize()}")
    print("                       hp:| FULL")
    print(f"          {chosen_battle_monster["name"].upper()} used {chosen_battle_move["move"].upper()}")
    print(f"name:|{chosen_battle_monster["name"].capitalize()}")
    print("  hp:| FULL")
    time.sleep(3)

    #displays the battle screen where the player has won
    if chosen_battle_move["power"] > opponent_battle_move["power"]:

        print("<<============================================")
        print(f"{opponent_battle_monster["name"].upper()} FAINTED!")
        print(f"                     name:|{opponent_battle_monster["name"].capitalize()}")
        print("                       hp:| 0")


        print(f"name:|{chosen_battle_monster["name"].capitalize()}")
        print("  hp:| FULL")


        print(f"{username} won!")

        has_player_won = True

    #displays the battle screen where the player has drawn, which results in a loss
    elif chosen_battle_move["power"] == opponent_battle_move["power"]:

        print("<<============================================")
        print(f"                     name:|{opponent_battle_monster["name"].capitalize()}")
        print("                       hp:| FULL")

        print(f"name:|{chosen_battle_monster["name"].capitalize()}")
        print("  hp:| FULL")

        print("\nBut nothing happened!")
        time.sleep(1)
        print("A stalemate...which counts as a loss")

        has_player_won = False

    #displays the battle screen where the player has lost
    else:
        print("\n<<============================================")
        print(f"                     name:|{opponent_battle_monster["name"].capitalize()}")
        print("                       hp:| FULL ")

        print(f"          {chosen_battle_monster["name"].upper()} FAINTED!")
        print(f"name:|{chosen_battle_monster["name"].capitalize()}")
        print("  hp:| 0")
        print(f"\n{username} lost!")

        has_player_won = False

    return has_player_won


def monster_log(has_player_won, chosen_monster_nums_list, opponent_monster_nums_list, monster_dict, name= "Opponent"):
    '''
    This function saves the battle outcome and the names of the player's and opponent's monster to a .txt file.
    :param username:
    :param has_player_won:
    :param chosen_monster_dict:
    :param opponent_monster_dict:
    :return:
    '''
    time.sleep(2)

    #as the first call of monster_log() is by the player's monster, the print statement on the game screen is shown to the Player.
    #since we the script is using the name variable for the if statements the Player's username argument is used to trigger
    #the player's monster being printed first.  The monster-log.txt file is opened in 'w' mode to overwrite a previous iteration of the game.
    if name != "Opponent":
        print("\n=============================================\n||           MONSTER-LOG UPDATED           ||\n=============================================")
        time.sleep(1)
        print(f"{name} has CAUGHT {len(chosen_monster_nums_list)} monsters and has SEEN {len(opponent_monster_nums_list)} monsters!")

        #creates and prints the pokedex.txt
        with open("monster-log.txt", "w+") as f:
            f.write(f"\n===================================================>>>\n   {name.upper()}'s MONSTER-LOG     \n===================================================>>>")

            if has_player_won == True:
                f.write("\n\nBattle Log: Winner!")
            else:
                f.write("\n\nBattle Log: Loser :(")

            f.write("\n\n==========================")
            f.write("\n||    Monsters Caught   ||")
            f.write("\n==========================")

    #since no username has been passed to the function, the default is used which trigger this if statement.
    #the file is opened in 'a+' mode I want to append to the Player's monster data not overwrite it.
    if name == "Opponent":
        with open("monster-log.txt", "a+") as f:
                f.write("\n\n========================")
                f.write("\n||    Monsters Seen   ||")
                f.write("\n========================")

    with open("monster-log.txt", "a+") as f:
        #this section loops through the monster selected in the game and prints their stats using list slicing
        #open() is using append mode as I want to append this information
        for i in range(3):

            f.writelines(f"\n\n  ===> {monster_dict[f"monster_{i + 1}"]["name"].upper()} <===")

            #as I need to access pairs of indicies eg. 1: 2, 3: 4. I have created two sliced lists that selects every
            #second index so 1, 3, 5... then from index one so 2, 4, 6... etc.
            #these are then paired together when written to the file.
            for stat in range(5):
                stats = monster_dict[f"monster_{i + 1}"]["stats"]
                stats_name_list = stats[::2]
                stats_strength_list = stats[1::2]

                f.write(f"\n  - {stats_name_list[stat]}: {stats_strength_list[stat]}")


def main():
    '''
    This function contains the game logic and runs each of the other functions in the game.
    :return:
    '''
    #runs the player introduction
    intro()

    #uses time.sleep() to make the game more user-friendly and engaging
    time.sleep(1)

    #asks the player their name to then use in a comical username generator
    username = input("What is your name?: ")


    #asks the player to input 3 numbers to select their monster
    chosen_monster_nums_list = [int(num) for num in (input("\n\nIT'S TIME TO CHOOSE YOUR MONSTER! \nchoose 3 numbers between 1 - 151 \nseparated by commas (,): ")).split(",")]


    #returns the player's monster's data to a dictionary
    chosen_monster_dict = get_monster(chosen_monster_nums_list, username)

    #the opponent chooses their monster (random numbers generated)
    opponent_monster_nums_list = get_opponent_monster_nums()

    #a dictionary is created of the opponent's monster's data
    opponent_monster_dict = get_monster(opponent_monster_nums_list)

    #both the player and opponent select the monster they wish to battle with (input for player, random number generated for opponent)
    chosen_battle_monster, opponent_battle_monster = get_battle_monster(username, chosen_monster_dict, opponent_monster_dict)

    #displays to the player their monster's moves and gets the player's chosen battle move
    chosen_battle_move = get_battle_move(chosen_battle_monster, name=username)

    # generates random number (1, 2 or 3)
    opponent_battle_move_num = random.randint(1, 3)

    #gets the opponent's battle move
    opponent_battle_move = get_battle_move(opponent_battle_monster, opponent_battle_move_num)

    #the monsters do battle (highest move power wins) and the result is returned
    has_player_won = battle(username, chosen_battle_monster, opponent_battle_monster, chosen_battle_move, opponent_battle_move)

    #a .txt file is created with battle outcome, and lists of the player's and opponent's monster and stats
    monster_log(has_player_won, chosen_monster_nums_list, opponent_monster_nums_list, chosen_monster_dict, username)
    monster_log(has_player_won, chosen_monster_nums_list, opponent_monster_nums_list, opponent_monster_dict)

    play_again = input("Would you like to play again? (y/n): ")

    return play_again

#this stops another script using part of this script from executing this script from another .py file.
if __name__ == "__main__":

    #adds a while loop to allow the player to play again
    play_again = "y"
    while play_again == "y":
        play_again = main()
