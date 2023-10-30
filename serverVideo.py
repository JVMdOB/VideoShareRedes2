import socket
import threading
import pickle 
# from pynat import get_ip_info

class Servidor:
    def __init__(self) -> None:
        # informacoes do servidor
        self.PORTA = 9500
        self.HOST = '0.0.0.0'
        self.registros = []

    def cadastra_usuario(self, conn, addr):
        reg = {"ip":addr[0], "port":addr[1]}
        conn.send(pickle.dumps("Digite seu nome de usuário"))
        

# a = get_ip_info()
# print(a)



# Configurações do servidor
HOST = '0.0.0.0'  # Para aceitar conexões de qualquer IP
PORT = 8080
MAX_CONNECTIONS = 10  # Número máximo de conexões simultâneas

# Lista para armazenar as conexões dos clientes
connections = []

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        # Faça alguma coisa com os dados recebidos, por exemplo, imprimir na tela
        print(data)
    client_socket.close()

# Configuração do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_CONNECTIONS)

print(f"Servidor escutando em {HOST}:{PORT}")

while True:
    client_socket, addr = server.accept()
    print(f"Conexão aceita de {addr[0]}:{addr[1]}")
    
    # Inicialize uma nova thread para lidar com o cliente
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()

