import RPi.GPIO as GPIO
import threading
import time
import os
import subprocess

DEBOUNCE_SW = 500                                           # debouncing for push button
DEBOUNCE_RO =   1                                           # debouncing for rotary encoder
VOL_STEP    =   5                                           # volume step (%)

# define interrupt events

lockRotary = threading.Lock()                               # interrupt lock for rotary switch

GPIO.setmode( GPIO.BCM)          

# volume rotary settings
GP_RO_VOL_SW = 17                                           # volume GPIO pin rotary SW
GP_RO_VOL_CL = 14                                           # volume GPIO pin rotary CLK
GP_RO_VOL_DT = 15                                           # volume GPIO pin rotary DT

GPIO.setup( GP_RO_VOL_SW, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup( GP_RO_VOL_CL, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup( GP_RO_VOL_DT, GPIO.IN, pull_up_down = GPIO.PUD_UP)

volData = ( GPIO.input( GP_RO_VOL_CL) << 3) + ( GPIO.input( GP_RO_VOL_DT) << 2)

# volume switch function
def event_VOL_SW( pin): 
    subprocess.call( ['mpc', 'toggle'])

# volume rotary function
def event_VOL_RO( pin):
    global volData, lockRotary

    cl = GPIO.input( GP_RO_VOL_CL)                          # read clock pin
    dt = GPIO.input( GP_RO_VOL_DT)                          # read data  pin

    volData = ( cl << 3) + ( dt << 2) + ( volData >> 2)     # process pins (2 new bits / 2 old bits)
                                                            # 0010 = backward / 0001 = forward
    # print " data = " + format( volData, '04b')            # print pin data

    lockRotary.acquire()                                    # lock interupts
    if ( volData == 0b0010): subprocess.call( ['mpc', 'volume', '-' + str( VOL_STEP)])
    if ( volData == 0b0001): subprocess.call( ['mpc', 'volume', '+' + str( VOL_STEP)])
    lockRotary.release()                                    # free interupts

GPIO.add_event_detect( GP_RO_VOL_SW, GPIO.FALLING, callback = event_VOL_SW, bouncetime = DEBOUNCE_SW)
GPIO.add_event_detect( GP_RO_VOL_CL, GPIO.FALLING, callback = event_VOL_RO, bouncetime = DEBOUNCE_RO)
GPIO.add_event_detect( GP_RO_VOL_DT, GPIO.FALLING, callback = event_VOL_RO, bouncetime = DEBOUNCE_RO)

# track rotary settings
GP_RO_TRK_SW = 22                                           # track GPIO pin rotary SW
GP_RO_TRK_CL = 23                                           # track GPIO pin rotary CLK
GP_RO_TRK_DT = 24                                           # track GPIO pin rotary DT

GPIO.setup( GP_RO_TRK_SW, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup( GP_RO_TRK_CL, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup( GP_RO_TRK_DT, GPIO.IN, pull_up_down = GPIO.PUD_UP)

trkData =  ( GPIO.input( GP_RO_TRK_CL) << 3) + ( GPIO.input( GP_RO_TRK_DT) << 2)

# track switch function
def event_TRK_SW( pin): subprocess.call( ['mpc', 'toggle'])

# track rotary function
def event_TRK_RO( pin):
    global trkData, lockRotary

    cl = GPIO.input( GP_RO_TRK_CL)                          # read clock pin
    dt = GPIO.input( GP_RO_TRK_DT)                          # read data  pin

    trkData = ( cl << 3) + ( dt << 2) + ( trkData >> 2)     # process pins (2 new bits / 2 old bits)
                                                            # 0010 = backward / 0001 = forward

    # print " data = " + format( trkData, '04b')            # print pin data

    lockRotary.acquire()                                    # lock interupts
    if ( trkData == 0b0010): subprocess.call( ['mpc', 'prev'])
    if ( trkData == 0b0001): subprocess.call( ['mpc', 'next'])
    lockRotary.release()                                    # free interupts

# activate event functions
GPIO.add_event_detect( GP_RO_TRK_SW, GPIO.FALLING, callback = event_VOL_SW, bouncetime = DEBOUNCE_SW)
GPIO.add_event_detect( GP_RO_TRK_CL, GPIO.FALLING, callback = event_TRK_RO, bouncetime = DEBOUNCE_RO)
GPIO.add_event_detect( GP_RO_TRK_DT, GPIO.FALLING, callback = event_TRK_RO, bouncetime = DEBOUNCE_RO)

# main
time.sleep(30)                                              # wait for mpc running
subprocess.call( ['mpc', 'repeat', 'on'])                   # set mpc repeat mode

while True:
    time.sleep(1)                                           # release cpu
