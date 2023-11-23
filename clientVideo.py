import socket
import pickle
import cv2
import pyaudio
import threading

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

    def iniciar_videochamada(self, ip_destino, porta_destino):
        # Check if the call is accepted
        self.envia_msg("INVITE")
        resposta = self.recebe_msg()
        if resposta == "Chamada aceita":
            # Start capturing video
            cap = cv2.VideoCapture(0)
            # Start capturing audio
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            while True:
                # Capture video frame
                ret, frame = cap.read()
                # Capture audio frame
                audio_frame = stream.read(1024)
                # Serialize and send
                self.servidor.send(pickle.dumps((frame, audio_frame)))
                if self.recebe_msg() == "END_CALL":
                    break
            # Release the video capture and audio stream
            cap.release()
            stream.stop_stream()
            stream.close()
            p.terminate()
        else:
            print("Chamada rejeitada")

    def receber_videochamada(self):
        # Start playing audio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)
        while True:
            # Receive and deserialize
            frame, audio_frame = pickle.loads(self.servidor.recv(1024))
            # Play video
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # Play audio
            stream.write(audio_frame)
            if self.recebe_msg() == "END_CALL":
                break
          # Close the video window and audio stream
        cv2.destroyAllWindows()
        stream.stop_stream()
        stream.close()
        p.terminate()

    def encerrar_videochamada(self):
        # Enviar mensagem de encerramento para o par
        self.envia_msg("END_CALL")


ip_servidor = "localhost"  
server_porta = 9502

cliente = Client(ip_servidor, server_porta)