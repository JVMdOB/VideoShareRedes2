import socket
import pickle

class Client:

    def __init__(self, ip, porta):
        self.ip_servidor = ip
        self.porta_servidor = porta
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.connect((ip, porta))
        self.comunicacao_servidor()

    def envia_msg(self, msg):
        self.servidor.send(pickle.dumps(msg))
    
    def recebe_msg(self):
        while True:
            msg = pickle.loads(self.servidor.recv(1024))
            if msg != None:
                break	
        return msg

    def finaliza(self):
        self.servidor.close()
    
    def comunicacao_servidor(self):
        r = self.recebe_msg()
        while r != "2":
            if r == "1":
                self.envia_msg(input())
            else:
                print(r)
            r = self.recebe_msg()
        
        self.finaliza()

ip_servidor = "localhost"  
server_porta = 9500  

cliente = Client(ip_servidor, server_porta)