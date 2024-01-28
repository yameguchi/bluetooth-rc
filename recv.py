#!/usr/bin/env python3
"""
server application that uses RFCOMM sockets.
"""
import bluetooth
import struct

from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device, AngularServo, PWMOutputDevice
from time import sleep

# set up device pins for servo movements
Device.pin_factory = PiGPIOFactory()

# initialize angular servos
right_aileron = AngularServo(17, min_angle=0, max_angle=180)
right_aileron.angle = 120
left_aileron = AngularServo(18, min_angle=0, max_angle=180)
left_aileron.angle = 60

# initialize PWM pin for motor
pwmOutput = PWMOutputDevice(19, initial_value=0.05, frequency=50)

# initialize bluetooth sockets to receive flight variable values
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# advertise server so client can see
bluetooth.advertise_service(server_sock, "receiver", service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            # protocols=[bluetooth.OBEX_UUID]
                            )

print("Waiting for connection on RFCOMM channel", port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from", client_info)

try:
    while True:
        data = client_sock.recv(20)
        thrust, roll, pitch = struct.unpack('=idd', data)
        if not data:
            break

        # adjust servo angles for pitch
        right_aileron_pitch = 120 - ((0.5 - pitch) * 2) * 30
        left_aileron_pitch = 60 + ((0.5 - pitch) * 2) * 30

        # adjust servo angles for roll       
        right_aileron.angle = right_aileron_pitch + ((0.5 - roll) * 2) * 30
        left_aileron.angle = left_aileron_pitch + ((0.5 - roll) * 2) * 30

        pwmOutput.value = 0.05 + (0.05 * thrust/10)

        print(right_aileron.angle, left_aileron.angle)

except OSError:
    pass

print("Disconnected.")

# clean up
right_aileron_pitch = 90
left_aileron_pitch = 90
pwmOutput.value(0.05)

client_sock.close()
server_sock.close()
print("All done.")
