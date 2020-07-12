#! /usr/bin/python3

	#########################
	####     MODULES     ####
	#########################

import requests
import RPi.GPIO as GPIO
import time, os, signal, sys, operator
from bottle import route, run, template, post, request, tob
from io import BytesIO


	#########################
	####    FUNCTIONS   #####
	#########################

class Watcher:
    def __init__(self):
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            print('KeyBoardInterrupt')
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError: pass


@post('/post')
def do_post():
    msg = ''
    GPIO.setwarnings(False)          #Turn off GPIO warning
    GPIO.setmode(GPIO.BOARD)         #Option mode to locate pin as number on board
    GPIO.setup(11, GPIO.IN)          #Set GPIO pin PIR motion sensor as input
    previousstate = 0
    currentstate= 0
    def notif(msg):
        API_ENDPOINT = "https://api.getnotify.me/submit"
        API_KEY = "nm8c6807d214"
        API_SECRET = "sce6043aba2f"
        data = {'message':msg}
        r = requests.post(url = API_ENDPOINT, json=data, auth=(API_KEY, API_SECRET))
        print(msg)
        
    try:
       # print("Waiting for PIR to settle...")
       # print("")
       # while GPIO.input(11) == 1:
       #     currentstate = 0
       # print("OK")
       # print("")
        print("Starting detection:")
        print("")
        body = request.body.read()
        print(body)
        while True:
            currentstate = GPIO.input(11) 
            if currentstate == 1 and previousstate == 0:
                print("Motion detected!")
                previousstate = 1
                msg = 'Non, il y a quelqu\'un'
                notif(msg)
                print("Wait ... ")
                time.sleep(30)
            elif currentstate == 0 and previousstate == 1:
                print('Ready again')
                previousstate = 0
                msg = 'Attend, il y a peut être encore quelqu\'un'
                notif(msg)
                time.sleep(0.01)
            else:
                print("Empty")
                msg = 'Oui, tu peux y aller'
                time.sleep(0.01)
                print('notif')
                notif(msg)
                time.sleep(5)
    except KeyboardInterrupt:
        print("Quit")
        GPIO.cleanup()
        Watcher.kill()
    return 

def main():

    #########################
    ####  INITIALIZATION ####
    #########################

    print("Start")
    print("")
    body = ''
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)

    #########################
    ####     PROCESS    #####
    #########################
	
    Watcher()
    run(host='0.0.0.0', port=8080)
	
if __name__ == "__main__":
    main()
	
