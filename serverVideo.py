import socket
import threading
import pickle
from bcrypt import hashpw, gensalt, checkpw

class Servidor:
    def __init__(self) -> None:
        # informacoes do servidor
        self.PORTA = 9500
        self.HOST = '0.0.0.0'
        self.registros = []

    def envia_msg(self, conn, msg):
        conn.send(pickle.dumps(msg))

    def recebe_msg(self, conn):
        while True:
            msg = pickle.loads(conn.recv(1024))
            if msg != None:
                break	
        return msg
    
    def envia_pergunta(self, conn, msg):
        """Envia msg ao usuario e aguarda resposta"""
        self.envia_msg(conn, msg)
        return self.recebe_msg(conn)
    
    def busca_usuario(self, chave: str, busca: str) -> dict:
        """
        Retorna o primeiro usuário com o termo {busca} no seu campo {chave}.
        Retorna None caso não haja
        """
        for user in self.registros:
            if user.get(chave) == busca:
                return user
        return None

    def cadastra_usuario(self, conn: socket.socket, addr: str) -> None:
        reg = {"ip":addr[0], "port":addr[1]}
        nome = self.envia_pergunta(conn, "Digite seu nome de usuário ou \"Sair\" para cancelar:")
        if nome.lower() == 'sair':
            return
        user = self.busca_usuario("nome", nome)
        if user:
            self.envia_msg(conn, "Nome já cadastrado! Tente de novo.")
            return self.cadastra_usuario(conn,addr)
        reg["nome"] = nome
        senha = self.envia_pergunta(conn, "Digite uma senha para o usuário ou \"Sair\" para cancelar.")
        while len(senha) <= 3:
            self.envia_msg("A senha deve conter no mínimo três caracteres.")
            senha = self.envia_pergunta(conn, "Digite uma senha para o usuário ou \"Sair\" para cancelar.")

        if senha.lower() == "sair":
            return
        salt = gensalt()
        reg['senha'] = hashpw(senha.encode(), salt)
        confirmacao = self.envia_pergunta(conn, "Confirme a senha ou digite \"Sair\"")
        while not checkpw(confirmacao.encode(), reg['senha']):
            if confirmacao.lower() == "sair":
                return
            confirmacao = self.envia_pergunta(conn, "As senhas não batem. Tente novamente ou \"Sair\" para cancelar ")
        self.envia_msg(conn, "Cadastro concluído com sucesso.")
        self.registros.append(reg)
        

    def exibe_usuarios(self, conn: socket.socket) -> None:
        """Exibe para o usuário solicitante todos os usuários cadastrados no sistema."""
        usuarios_string = ""
        if len(self.registros == 0):
            usuarios_string = "Não há usuários cadastrados por enquanto"
        else:
            usuarios_string = "NOME \t\t IP \t\t PORTA\n"
            for usuario in self.registros:
                usuarios_string += f"{usuario.get('nome')}\t\t{usuario.get('ip')}\t\t{usuario.get('port')}\n"
        self.envia_msg(conn, usuarios_string)
    
    def deleta_usuario(self, conn: socket.socket, addr: str) -> None: # criar tbm atualiza_usuario
        """Deleta usuário ou pelo IP ou pelo nome de usuario e senha"""
        user = self.busca_usuario("ip", addr[0])
        if user:
            resp = self.envia_pergunta(conn, f"Usuário {user['nome']} com IP {user['ip']} detectado. Deseja excluir seu usuário? Digite 'Sim' para excluir")
            if resp.lower() == 'sim':
                self.registros.remove(user)
        else:
            nome = self.envia_pergunta(conn, "Nenhum usuário encontrado para o seu IP. Para excluir um usuário por nome, digite o nome de usuário agora, ou SAIR para encerrar.")
            if nome.lower() != 'sair':
                user = self.busca_usuario("nome", nome)
                if not user:
                    self.envia_msg(conn, "Nenhum usuário encontrado com este nome.")
                    return self.deleta_usuario(conn, addr)
                else:
                    senha = ""
                    senha = self.envia_pergunta(conn, "Usuário encontrado. Digite a senha para confirmar exclusão ou \"Sair\" para cancelar.")
                    while not checkpw(senha.encode(), user.get('senha')):
                        self.envia_msg(conn, "Senha incorreta")
                        senha = self.envia_pergunta(conn, "Digite a senha para confirmar exclusão ou \"Sair\" para cancelar.")
                    self.registros.remove(user)

                    

            

        




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
    print(type(client_socket))
    print(f"Conexão aceita de {addr[0]}:{addr[1]}")
    
    # Inicialize uma nova thread para lidar com o cliente
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()

