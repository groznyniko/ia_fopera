import socket
import messages
import protocol
from random import randrange
import time

host = "localhost"
port = 15555

class Player():

    def __init__(self):

        self.end = False;
        self.old_question = ""
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        self.handlers = {
            "Information" : self.handle_informations ,
            "Question": self.handle_questions
        }

    def connect(self):
        self.socket.connect("./server")

    def reset(self):
        self.socket.close()

    def answer(self):
        r = messages.Response(str(randrange(2)))
        protocol.send_one_message(self.socket, r.toJson())

    def handle_questions(self, question):
        self.answer()

    def handle_informations(self, information):
        if "Score final" in information:
            # self.end = True
            print("Partie finie")

    def handle_message(self, message):
        handler = self.handlers[message.type]
        handler(message.content)


    def run(self):

        self.connect()

        while self.end is not True:
            message = protocol.recv_one_message(self.socket)
            self.handle_message(messages.deserialize(message))


p = Player();

p.run()

