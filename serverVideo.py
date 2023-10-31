import socket
import threading
import pickle
from bcrypt import hashpw, gensalt, checkpw
from time import sleep
import json

class Servidor:
    def __init__(self) -> None:
        # informacoes do servidor
        self.PORTA = 9500
        self.ARQ_USUARIOS = "usuarios.json"
        self.HOST = '0.0.0.0'
        maximo = 10
        self.registros = self.carrega_json()

        # inicializando o servidor
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.HOST, self.PORTA))
        self.servidor.listen(maximo)

    def salva_json(self):
        if len(self.registros) > 0:
            with open(self.ARQ_USUARIOS, 'w') as f:
                json.dump(self.registros, f, indent=4)
    
    def carrega_json(self) -> list:
        # retorna a lista de usuários caso haja, ou uma lista vazia caso contrário
        try:
            with open(self.ARQ_USUARIOS, 'r') as f:
                return json.load(f)
        except:
            return []

    def envia_msg(self, conn, msg):
        msg = msg 
        conn.send(pickle.dumps(msg))

    def recebe_msg(self, conn):
        while True:
            msg = pickle.loads(conn.recv(1024))
            if msg != None:
                break	
        return msg
    
    def envia_pergunta(self, conn, msg):
        """Envia mensagem ao usuario e retorna resposta"""
        
        self.envia_msg(conn, msg)
        sleep(0.5)
        self.envia_msg(conn, "1") # sinal de pergunta para o cliente
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
        """Cria um usuário e armazena na lista de usuários. Pede informações de nome de usuário, senha, e porta. Também armazena o IP da conexão."""
        
        reg = {"ip":addr[0], "porta":addr[1]}
        nome = self.envia_pergunta(conn, "Digite o nome de usuário que deseja cadastrar ou \"Sair\" para cancelar:\n")
        if nome.lower() == 'sair':
            return
        user = self.busca_usuario("nome", nome)
        if user:
            self.envia_msg(conn, "Nome já cadastrado! Tente de novo.\n")
            return self.cadastra_usuario(conn,addr)
        reg["nome"] = nome
        p = self.envia_pergunta(conn, f"Você está atualmente utilizando a porta {addr[1]}. Caso queira cadastrar esta porta digite 0, caso contrário digite o número da porta que deseja cadastrar.\n")
        if p != "0":
            try:
                port = int(p)
                reg["porta"] = port
            except:
                self.envia_msg("Valor inválido de porta. Reiniciando cadastro.")
                return self.cadastra_usuario(conn, addr)

        senha = self.envia_pergunta(conn, "Digite uma senha para o usuário ou \"Sair\" para cancelar.\n")
        while len(senha) <= 3:
            self.envia_msg(conn, "A senha deve conter mais de três caracteres.\n")
            senha = self.envia_pergunta(conn, "Digite uma senha para o usuário ou \"Sair\" para cancelar.\n")
        if senha.lower() == "sair":
            return
        
        salt = gensalt() # gerando um salt para o hash da senha
        reg['senha'] = hashpw(senha.encode(), salt) # armazenando o hash a fim de evitar senhas diretamente armazenadas
        confirmacao = self.envia_pergunta(conn, "Confirme a senha ou digite \"Sair\"\n")
        while not checkpw(confirmacao.encode(), reg['senha']): # verificando se senhas são iguais
            if confirmacao.lower() == "sair":
                return
            confirmacao = self.envia_pergunta(conn, "As senhas não batem. Tente novamente ou \"Sair\" para cancelar\n")
        
        self.envia_msg(conn, "Cadastro concluído com sucesso.\n")
        self.registros.append(reg) 
        

    def exibe_usuarios(self, conn: socket.socket) -> None:
        """Exibe para o usuário solicitante todos os usuários cadastrados no sistema."""
        usuarios_string = ""
        if len(self.registros) == 0:
            usuarios_string = "Não há usuários cadastrados por enquanto\n"
        else:
            usuarios_string = "NOME \t\t\t IP \t\t\t PORTA\n"
            for usuario in self.registros:
                usuarios_string += f"{usuario.get('nome')}\t\t\t{usuario.get('ip')}\t\t\t{usuario.get('porta')}\n"
        self.envia_msg(conn, usuarios_string)
    
    def deleta_usuario(self, conn: socket.socket, addr: str) -> None: # TODO:criar tbm atualiza_usuario
        """Deleta usuário ou pelo IP ou pelo nome de usuario e senha"""
        user = self.busca_usuario("ip", addr[0])
        if user:
            resp = self.envia_pergunta(conn, f"Usuário {user['nome']} com IP {user['ip']} detectado. Deseja excluir seu usuário? Digite 'Sim' para excluir\n")
            if resp.lower() == 'sim':
                self.registros.remove(user)
        else:
            nome = self.envia_pergunta(conn, "Nenhum usuário encontrado para o seu IP. Para excluir um usuário por nome, digite o nome de usuário agora, ou \"Sair\" para encerrar.\n")
            if nome.lower() != 'sair':
                user = self.busca_usuario("nome", nome)
                if not user:
                    self.envia_msg(conn, "Nenhum usuário encontrado com este nome.\n")
                    return self.deleta_usuario(conn, addr)
                else:
                    senha = ""
                    senha = self.envia_pergunta(conn, "Usuário encontrado. Digite a senha para confirmar exclusão ou \"Sair\" para cancelar.\n")
                    while not checkpw(senha.encode(), user.get('senha')):
                        self.envia_msg(conn, "Senha incorreta")
                        senha = self.envia_pergunta(conn, "Digite a senha para confirmar exclusão ou \"Sair\" para cancelar.\n")
                    self.registros.remove(user)
                    self.envia_msg(conn, "Usuário excluído com sucesso.\n")
    
    def finaliza(self, conn):
        self.envia_msg(conn, "Encerrando.\n")
        self.envia_msg(conn, "2") # sinal de saída para o cliente
        conn.close()

    def cliente_menu(self, conn: socket.socket, addr : list):
        """Gerencia a conexão inicial com o cliente e """
        # Enviando mensagem inicial a cliente e aguardando resposta
        msg_inicial = """Seja bem vindo!
Para utilizar o sistema, digite o número associado a opção que deseja:
        1 - Se cadastrar no sistema
        2 - Checar usuários cadastrados
        3 - Deletar usuário cadastrado
        
Ou digite \"Sair\" para sair.\n"""
        try:
            # Verificando resposta do usuário e direcionando para função específica
            resposta = self.envia_pergunta(conn, msg_inicial)
            while resposta.lower() != "sair":
                if resposta == "1":
                    self.cadastra_usuario(conn, addr)
                elif resposta == "2":
                    self.exibe_usuarios(conn)
                elif resposta == "3":
                    self.deleta_usuario(conn, addr)
                else:
                    self.envia_msg(conn, "Resposta inválida. Digite apenas o número desejado ou \"Sair\"\n")
                resposta = self.envia_pergunta(conn, msg_inicial)
        except:
            self.finaliza(conn)
        self.finaliza(conn)

                    

            

        


def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        # Faça alguma coisa com os dados recebidos, por exemplo, imprimir na tela
        print(data)
    client_socket.close()

# Configuração do servidor


servidor = Servidor()
print(f"Servidor escutando em {servidor.HOST}:{servidor.PORTA}")
while True:
    try:
        client_socket, addr = servidor.servidor.accept()
        print(f"Conexão aceita de {addr[0]}:{addr[1]}")
        
        # Inicialize uma nova thread para lidar com o cliente
        client_handler = threading.Thread(target=servidor.cliente_menu, args=(client_socket,addr))
        client_handler.start()
    except:
        pass

