from time import sleep
from i2c_lcd1602 import Screen
from gpiozero import Button, RotaryEncoder
from signal import pause

'''
To run the program, the necessary dependancies are gpiozero, RPi.GPIO, stopwatch.py
RPi.GPIO is preinstalled
sudo pip install stopwatch.py
sudo pip3 install gpiozero
'''

setup = False
screen = Screen(bus=1, addr=0x3f, cols=16, rows=2)
button = Button(4, bounce_time=1)
rot_but = Button(22)
rotary = RotaryEncoder(17, 27, max_steps=0)

turn_phases = ['Untap', 'Upkeep', 'Draw', 'Main Phase 1', 'Begin Combat', 'Declare Attacker',
               'Declare Blockers', 'Combat Damage', 'End Combat', 'Main Phase 2', 'End Phase']

left = False
right = False


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

    menu = 0
    turns = 1
    game = True
    player_turn = 0
    current_phase = 0
    life_editor = False
    player_life_editor = 0

    while game == True:

        rotary.when_rotated_clockwise = turn_right
        rotary.when_rotated_counter_clockwise = turn_left

        if menu == 0:
            '''
            The turn system works by increasing the player and current phase counters and displaying the relevant text.
            The starting if statements determine when any actions have been detected by the sensors and to increase the counter variables accordingly.
            Because the variables here uses for counting dont change accross the rest of the file, it is saved when transitioning between menus 
            '''

            if player_turn >= len(player_life):
                player_turn = 0

            if rot_but.is_pressed:
                current_phase = 0
                player_turn = player_turn + 1
                turns = turns + 1
                sleep(0.5)

            if current_phase == len(turn_phases):
                current_phase = 0
                player_turn = player_turn + 1
                turns = turns + 1

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
            if rot_but.is_pressed:
                life_editor = True
            
            if life_editor == False:
                if right == True:
                    if player_life_editor < (len(player_life) - 1):
                        player_life_editor = player_life_editor + 1
                        right = False

                if left == True:
                    if player_life_editor > 0:
                        player_life_editor = player_life_editor - 1
                        left = False
                screen.cursorTo(0, 1)
                screen.display_data("Edit Player Life")
                screen.cursorTo(1, 1)
                screen.display_data(f"{list(player_life.keys())[player_life_editor]}")
            else:
                screen.cursorTo(0, 1)
                screen.display_data(f"{list(player_life.keys())[player_life_editor]}'s Life")
                screen.cursorTo(1, 1)
                screen.display_data(str(player_life[player_life_editor]))

        elif menu == 2:
            screen.cursorTo(0, 1)
            screen.display_data("Game Statistics")
            screen.cursorTo(1, 1)
            screen.display_data(f"Turn {turns} Time {}")

        else:
            menu = 0

        if button.is_pressed == True:
            menu = menu + 1
            sleep(0.5)
        for x, life in player_life.items():
            if life == 0:
                game == False


def end():
    '''
    Displays text on screen for games results
    '''

    print("Thank you so much a-for-to playing my game")


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
