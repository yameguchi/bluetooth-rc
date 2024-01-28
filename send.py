#!/usr/bin/env python3
"""
client application that uses RFCOMM sockets intended
for use with rfcomm-server.
"""

import sys
import bluetooth
import pygame
import struct

addr = None

if len(sys.argv) < 2:
    print("No device specified. Searching all nearby bluetooth devices for "
          "the receiver service...")
else:
    addr = sys.argv[1]
    print("Searching for receiver on {}...".format(addr))

# search for the receiver service
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
service_matches = bluetooth.find_service(uuid=uuid, address=addr)

if len(service_matches) == 0:
    print("Couldn't find the receiver service.")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("Connecting to \"{}\" on {}".format(name, host))

# Create the client socket
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

print("Connected. Type something...")
"""while True:
    data = input()
    if not data:
        break
    sock.send(data)

"""

# set up pygame
pygame.init()
screen = pygame.display.set_mode((1920, 1200)) #2240, 1400
screen.fill("black")
clock = pygame.time.Clock()
running = True

# initialize mouse
pygame.mouse.set_pos([1920 / 2, 1200 / 2])

# initialize flight variables
thrust = 0          # scroll y-axis
roll = 0            # mouse x-axis
pitch = 0           # mouse y-axis

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEWHEEL:
            # down scroll
            if event.y < 0:
                if thrust <= 9:
                    thrust += 1
            # up scroll
            else:
                if thrust > 0:
                    thrust -= 1

    mouse_x, mouse_y = pygame.mouse.get_pos()
    roll = round(mouse_x / 1920, 2) #2240
    pitch = round(mouse_y / 1200, 2)

    print(thrust, roll, pitch)

    # send data to pi zero
    data = struct.pack('=idd', thrust, roll, pitch)
    sock.send(data)

    clock.tick(60)  # limits FPS to 60

pygame.quit()
sock.close()
