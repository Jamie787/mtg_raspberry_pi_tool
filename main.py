from time import sleep
from i2c_lcd1602 import Screen
from gpiozero import Button, RotaryEncoder
from signal import pause
from stopwatch import Stopwatch
from datetime import timedelta
from math import floor

'''
To run the program, the necessary dependancies are gpiozero, RPi.GPIO, ez-stopwatch
RPi.GPIO is preinstalled
sudo pip3 install ez-stopwatch
sudo pip3 install gpiozero
'''

setup = False
screen = Screen(bus=1, addr=0x3f, cols=16, rows=2)
button = Button(4, bounce_time=1)
rot_but = Button(22)
rotary = RotaryEncoder(17, 27, max_steps=0)
turn_timer = Stopwatch()
game_timer = Stopwatch()

turn_phases = ['Untap', 'Upkeep', 'Draw', 'Main Phase 1', 'Begin Combat', 'Declare Attacker',
               'Declare Blockers', 'Combat Damage', 'End Combat', 'Main Phase 2', 'End Phase']

left = False
right = False


def dict_key_name(dict_name: str, key_of_dict: int):

    key_name = list(dict_name.keys())[key_of_dict]
    return key_name


def longest_time(turn_time: float):
    global longest_turn_time

    if turn_time > longest_turn_time:
        longest_turn_time = turn_time


def avg_turn_length():
    sum_of_turns = 0
    for turn in avg_turn_time:
        sum_of_turns = sum_of_turns + turn

    avg_time = sum_of_turns / len(avg_turn_time)
    return avg_time


def turn_left():
    global left
    left = True


def turn_right():
    global right
    right = True


def start():
    '''
    Sets up the game for the game type
    Asks for the amount of players and lives per player and makes them global
    Once the data is gathered, the function is ended 
    '''

    global player_amount
    global lives

    screen.enable_backlight()
    screen.cursorTo(0, 1)

    menu = 0

    while setup == False:
        if menu == 0:
            screen.cursorTo(0, 1)
            screen.display_data("How many players")

            player_amount = abs(rotary.steps)
            screen.cursorTo(1, 1)
            screen.display_data(str(player_amount))

            if rot_but.is_pressed == True:
                menu = menu + 1
                sleep(0.1)

        elif menu == 1:
            screen.cursorTo(0, 1)
            screen.display_data("Starting Lives")

            lives = rotary.steps
            screen.cursorTo(1, 1)
            screen.display_data(str(lives))

            if rot_but.is_pressed == True:
                menu = menu + 1
                sleep(0.1)

        else:
            return


def initialise_players():
    '''
    Uses the global variables from the previous function to create a global dictionary
    '''

    global player_life
    player_life = {}

    for x in range(player_amount):
        player_life[f"Player {x + 1}"] = lives


def main():
    '''
    Main function for displaying menu data
    The menu variable keeps track of the current menu state selected and changes the menu when the button is pressed
    Menu 0 controlls the current turn and which player it is
    Menu 1 Adjusts the current lives of all players
    Menu 2 Displays statistics and allows ending game early or restarting
    '''

    sleep(1)

    global player_life
    global turns
    global left
    global right
    global ending
    global longest_turn_time
    global avg_turn_time

    menu = 0
    turns = 1
    game = True
    player_turn = 0
    current_phase = 0
    life_editor = False
    player_life_editor = 0

    stats_menu = 0
    action_menu = 0
    actions = ["Forfeit?", "Restart?"]
    longest_turn_time = 0
    avg_turn_time = []

    game_timer.start()
    turn_timer.start()

    while game == True:

        rotary.when_rotated_clockwise = turn_right
        rotary.when_rotated_counter_clockwise = turn_left
        statistic_list = [f"Turn: {turns}", f"TurnTime {timedelta(seconds=floor(turn_timer.time_elapsed))}",
                          f"GameTime {timedelta(seconds=floor(game_timer.time_elapsed))}"]

        if menu == 0:
            '''
            The turn system works by increasing the player and current phase counters and displaying the relevant text.
            The starting if statements determine when any actions have been detected by the sensors and to increase the counter variables accordingly.
            Because the variables here uses for counting dont change accross the rest of the file, it is saved when transitioning between menus 
            '''

            if player_turn >= len(player_life):
                player_turn = 0

            if rot_but.is_pressed:
                turn_timer.stop()
                longest_time(turn_timer.time_elapsed)
                avg_turn_time.append(turn_timer.time_elapsed)
                turn_timer.reset()
                current_phase = 0
                player_turn = player_turn + 1
                turns = turns + 1
                sleep(0.5)
                turn_timer.start()

            if current_phase == len(turn_phases):
                turn_timer.stop()
                longest_time(turn_timer.time_elapsed)
                avg_turn_time.append(turn_timer.time_elapsed)
                turn_timer.reset()
                current_phase = 0
                player_turn = player_turn + 1
                turns = turns + 1
                turn_timer.start()

            if right == True:
                current_phase = current_phase + 1
                right = False

            if left == True:
                print("there's no undo button in magic :))")
                left = False

            screen.cursorTo(0, 1)
            screen.display_data(
                f"{list(player_life.keys())[player_turn % len(player_life)]}'s turn")
            screen.cursorTo(1, 1)
            screen.display_data(turn_phases[current_phase % len(turn_phases)])

        elif menu == 1:
            if life_editor == False:
                if rot_but.is_pressed:
                    life_editor = True
                    sleep(0.2)

                if (right == True) and (player_life_editor < (len(player_life) - 1)):
                    player_life_editor = player_life_editor + 1
                    right = False
                else:
                    right = False

                if (left == True) and (player_life_editor > 0):
                    player_life_editor = player_life_editor - 1
                    left = False
                else:
                    left = False

                screen.cursorTo(0, 1)
                screen.display_data("Edit Player Life")
                screen.cursorTo(1, 1)
                screen.display_data(
                    f"{dict_key_name(player_life, player_life_editor)}")
            else:
                if rot_but.is_pressed:
                    life_editor = False
                    sleep(0.2)

                if left == True:
                    player_life[dict_key_name(player_life, player_life_editor)] = player_life[dict_key_name(
                        player_life, player_life_editor)] - 1
                    left = False

                if right == True:
                    player_life[dict_key_name(player_life, player_life_editor)] = player_life[dict_key_name(
                        player_life, player_life_editor)] + 1
                    right = False

                screen.cursorTo(0, 1)
                screen.display_data(
                    f"{dict_key_name(player_life, player_life_editor)}'s Life")
                screen.cursorTo(1, 1)
                screen.display_data(
                    str(player_life[dict_key_name(player_life, player_life_editor)]))

        elif menu == 2:
            screen.cursorTo(0, 1)
            screen.display_data("Game Statistics")

            if (right == True) and (stats_menu < 2):
                stats_menu = stats_menu + 1
                right = False
            else:
                right = False

            if (left == True) and (stats_menu > 0):
                stats_menu = stats_menu - 1
                left = False
            else:
                left = False

            screen.cursorTo(1, 1)
            screen.display_data(statistic_list[stats_menu])

        elif menu == 3:
            screen.cursorTo(0, 1)
            screen.display_data("Choose Action")

            if (right == True) and (action_menu < 1):
                action_menu = action_menu + 1
                right = False
            else:
                right = False

            if (left == True) and (action_menu > 0):
                action_menu = action_menu - 1
                left = False
            else:
                left = False

            screen.cursorTo(1, 1)
            screen.display_data(actions[action_menu])

            if (rot_but.is_pressed) and (action_menu == 0):
                game = False
                ending = "Forfeit"
            elif (rot_but.is_pressed) and (action_menu == 1):
                restart()

        else:
            menu = 0

        if button.is_pressed == True:
            menu = menu + 1
            sleep(0.2)

        player_life_copy = player_life.copy()

        for players_left, life in player_life_copy.items():
            if life == 0:
                screen.cursorTo(0, 1)
                screen.display_data(f"    {players_left}  ")
                screen.cursorTo(1, 1)
                screen.display_data("   Eliminated   ")
                player_life.pop(players_left)
                life_editor = False
                sleep(2)

        if len(player_life) == 1:
            ending = f"{dict_key_name(player_life, 0)} Won"
            game = False


def end():
    '''
    Displays text on screen for games results
    '''
    global right
    global left

    right = False
    left = False

    print("Thank you so much a-for-to playing my game")
    screen.cursorTo(0, 1)
    screen.display_data("    GAME OVER   ")
    screen.cursorTo(1, 1)
    screen.display_data(f"Ending: {ending}")
    sleep(3)
    screen.cursorTo(1, 1)
    screen.display_data(f"Turns: {turns}")
    sleep(5)
    screen.cursorTo(1, 1)
    screen.display_data(
        f"Time:    {timedelta(seconds=floor(game_timer.time_elapsed))}")
    sleep(5)
    screen.cursorTo(1, 1)
    screen.display_data(
        f"TurnLth: {timedelta(seconds=floor(longest_turn_time))}")
    sleep(5)
    screen.cursorTo(1, 1)
    screen.display_data(
        f"TurnAvg: {timedelta(seconds=floor(avg_turn_length()))}")
    sleep(5)

    option_list = ["  View Results  ", "    New Game    "]
    options = 0
    while True:
        rotary.when_rotated_clockwise = turn_right
        rotary.when_rotated_counter_clockwise = turn_left

        if (right == True) and (options == 0):
            options = options + 1
            right = False
        else:
            right = False
        if (left == True) and (options == 1):
            options = options - 1
            left = False
        else:
            left = False
        screen.cursorTo(0, 1)
        screen.display_data("  Choose Option ")
        screen.cursorTo(1, 1)
        screen.display_data(option_list[options])
        if (options == 0) and (rot_but.is_pressed == True):
            end()
        elif (options == 1) and (rot_but.is_pressed == True):
            restart()


def destroy():  # clears screen when interupted
    sleep(0.1)
    screen.cursorTo(0, 1)
    screen.display_data("                ")
    screen.cursorTo(1, 1)
    screen.display_data("                ")


def restart():
    '''
    Restarts the program when called
    '''

    import sys
    import os
    os.execv(sys.executable, ['python'] + sys.argv)


if __name__ == '__main__':
    start()
    initialise_players()
    main()
    end()
