##libraries/import modules
import asyncio
import pygame
from pygame.locals import *
import requests
import json
import time
# from lxml import html

##intialize pygame
pygame.init()
screen_width = 800
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))

##variables
Gravity = 0.05
player_obj = {
    "x": 50,
    "y": 300,
    "xvel": 0,
    "yvel": 0,
    "in_air": True,
    "connectionId": "-1",
    "seconds_played": 0
}
other_players = {}
keytracker = {"d": False, "a": False}
bg = (200, 200, 200)
screen.fill(bg)
pygame.display.update()
running = True
frame = 0
player_size = 75

##functions
async def server_post(player_data):
    response = requests.post(
        "http://localhost:8000/ServerPost", data=json.dumps(player_data)
    )
    return response.json()


def form_connection():
    response = requests.get("http://localhost:8000/Connect")
    print(f"Connection Id: {response.json()[0]}")  # debug
    player_obj["connectionId"] = response.json()[0]


async def await_server_post(playerdata):
    global other_players
    other_players = await server_post(playerdata)


def break_connection(connect_id):
    connect_data = f"[{connect_id}]"
    requests.post("http://localhost:8000/Quit", data=connect_data)


##load images and fonts
ninja_sprite = pygame.transform.scale(
    pygame.image.load("Assets/ninja_sprite_pygame.png"), (player_size, player_size)
)
pacman_sprite = pygame.transform.scale(
    pygame.image.load("Assets/pacman_sprite_pygame.png"), (player_size, player_size)
)
text_font_one_size = 30
text_font_one = pygame.font.SysFont("Comic Sans MS", text_font_one_size)
text_font_one_size /= 2

form_connection()  # connect to server before starting run loop

##continuous run loop
while running:
    startTime = time.time()
    if frame % 60 == 0:
        frame = 0
        asyncio.run(await_server_post(player_obj))
    pygame.time.delay(5)  # reduce for faster speed but more lag from event handling
    for event in pygame.event.get(eventtype=[KEYDOWN, QUIT, KEYUP]):
        # allow quit
        if event.type == pygame.QUIT:
            running = False
            break_connection(player_obj["connectionId"])
            continue
        # key listeners
        if event.type == pygame.KEYDOWN:
            if event.key == K_w and not player_obj["in_air"]:
                player_obj["yvel"] -= 5
                player_obj["in_air"] = True
            elif event.key == K_d:
                keytracker["d"] = True
            elif event.key == K_a:
                keytracker["a"] = True
            continue
        if event.type == pygame.KEYUP:  # redundant but keep for now
            if event.key == K_d:
                keytracker["d"] = False
            elif event.key == K_a:
                keytracker["a"] = False
            continue
    # apply keytracker
    if keytracker["d"]:
        player_obj["xvel"] += 0.025
    if keytracker["a"]:
        player_obj["xvel"] -= 0.025
    elif not keytracker["d"] and not keytracker["a"]:
        player_obj["xvel"] *= 0.99
        if abs(player_obj["xvel"]) < 0.01:
            player_obj["xvel"] = 0
    # gravity
    if player_obj["in_air"]:
        player_obj["yvel"] += Gravity
    # speed limit
    if player_obj["xvel"] > 1:
        player_obj["xvel"] = 1
    elif player_obj["xvel"] < -1:
        player_obj["xvel"] = -1
    if player_obj["yvel"] < -7:
        player_obj["yvel"] = -7
    # apply velocities
    player_obj["x"] += player_obj["xvel"]
    player_obj["y"] += player_obj["yvel"]
    # screen boundary
    if player_obj["x"] < 0:
        player_obj["x"] = 0
        player_obj["xvel"] = 0
    elif player_obj["x"] + player_size > screen_width:
        player_obj["x"] = screen_width - player_size
        player_obj["xvel"] = 0
    if player_obj["y"] < 0:
        player_obj["y"] = 0
        player_obj["yvel"] = 0
    elif player_obj["y"] + player_size > screen_height:
        player_obj["y"] = screen_height - player_size
        player_obj["yvel"] = 0
        player_obj["in_air"] = False
    screen.fill(bg)  # set background before adding sprites
    # update all other players
    for pl in other_players.keys():
        if pl == player_obj["connectionId"]:
            continue
        other_players[pl]["x"] += other_players[pl]["xvel"]
        other_players[pl]["y"] += other_players[pl]["yvel"]
        if other_players[pl]["x"] < 0:
            other_players[pl]["x"] = 0
            other_players[pl]["xvel"] = 0
        elif other_players[pl]["x"] + player_size > screen_width:
            other_players[pl]["x"] = screen_width - player_size
            other_players[pl]["xvel"] = 0
        if other_players[pl]["y"] < 0:
            other_players[pl]["y"] = 0
            other_players[pl]["yvel"] = 0
        elif other_players[pl]["y"] + player_size > screen_height:
            other_players[pl]["y"] = screen_height - player_size
            other_players[pl]["yvel"] = 0
            other_players[pl]["in_air"] = False
        if other_players[pl]["in_air"]:
            other_players[pl]["yvel"] += Gravity
        screen.blit(pacman_sprite, (other_players[pl]["x"], other_players[pl]["y"]))
        text_surface = text_font_one.render(str(round(other_players[pl]["seconds_played"])), False, (255, 0, 0))
        screen.blit(
            text_surface,
            (
                other_players[pl]["x"] + (player_size / 2) - (text_font_one_size * (len(str(other_players[pl]["seconds_played"])) / 2)),
                other_players[pl]["y"] - 10 - text_font_one_size
            )
        )
    # update canvas sprites
    screen.blit(ninja_sprite, (player_obj["x"], player_obj["y"]))
    text_surface = text_font_one.render(str(round(player_obj["seconds_played"])), False, (0, 0, 255))
    screen.blit(
        text_surface,
        (
            player_obj["x"] + (player_size / 2) - text_font_one_size * len(str(round(player_obj["seconds_played"]))) / 2,
            player_obj["y"] - 10 - text_font_one_size,
        )
    )
    pygame.display.update()
    frame += 1
    endTime = time.time()
    player_obj["seconds_played"] += (endTime - startTime)

pygame.quit()  # quit pygame before ending the program
