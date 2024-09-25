############################################################
# Primeiro Exercício Programa - Escalonador de Processos   #
# Disciplina: Sistemas Operacionais                        #
# Docente: Prof. Dr. Norton Trevisan Roman                 #
# Turma: 04                                                #
# Discentes:                                               #
#  Mariana Borges Araujo da Silva, NUSP: 14596342          #
#  Pedro Serrano Buscaglione, NUSP: 14603652               #
############################################################

#O Exercício Programa proposto tem como objetivo simular um Escalonador de Processos em um SO. Um escalonador tem como principal função
#Gerenciar a execução de múltiplos processos, tomando a decisão de qual processo, e por quanto tempo, será executado
#O escalonador tabém lida com bloqueios e trocas entre os processos
#A linguagem de programação utilizada nesse EP foi Python

#Classe BCP (Bloco de Controle de Processo)
class BCP:
    # O método __init__ é o construtor da classe. Ele é chamado automaticamente quando uma nova instância da classe é criada
    def __init__(self, nome_programa, prioridade, codigo_programa):

        # Inicializa o contador de programa, que indica a posição atual no código do programa. Começa em 0, indicando o início do código 
        self.contador_programa = 0

        # Estados possíveis: 'Executando', 'Pronto', 'Bloqueado'
        # Define o estado inicial do processo como 'Pronto'. O estado pode ser 'Executando', 'Pronto', ou 'Bloqueado'.
        self.estado = 'Pronto'  

        # Define a prioridade do processo. A prioridade influencia a ordem em que os processos são executados
        self.prioridade = prioridade
        
        # Inicializa o número de créditos do processo com a mesma prioridade
        # Os créditos são usados para determinar quanto tempo de CPU um processo tem antes de ser interrompido
        self.creditos = prioridade
       
        # Inicializa o registrador X do processo com 0. O registrador X é um dos registradores de uso geral no processo.
        self.registrador_x = 0
        
        # Inicializa o registrador Y do processo com 0. O registrador Y é outro registrador de uso geral no processo.
        self.registrador_y = 0
        
         # Define o código do programa do processo. Isso é uma lista ou outro tipo de estrutura que contém as instruções que o processo deve executar.
        self.codigo_programa = codigo_programa
       
        # Armazena o nome do programa associado a este processo. O nome é útil para identificação e gerenciamento dos processos.
        self.nome_programa = nome_programa

        # Inicializa o tempo de espera do processo com 0. Esse tempo representa quantos ciclos o processo deve esperar enquanto está bloqueado
        # O tempo será ajustado quando o processo realizar uma operação de E/S (quando o processo executa uma opração de E/S, ele entra em estado de Bloqueado
        # e é atribuido um valor a tempo_espera, indicando quanto tempo ele ficará Bloqueado)
        self.tempo_espera = 0  # Usado para processos bloqueados
        
#Classe que representa a Tabela de Processos
class TabelaProcessos:
    def __init__(self):
        self.processos = {} #Dicionário para armazenar BCPs com base no nome do processo 
    
    #Método que adiciona um processo na tabela
    def adicionar_processo(self, bcp):
        self.processos[bcp.nome_programa] = bcp 
    
    #Método que remove um processo na tabela
    def remover_processo(self, nome_programa):
        if nome_programa in self.processos:
            del self.processos[nome_programa]

    #Método que obtém o BCP de um processo pelo nome
    def obter_bcp(self, nome_programa):
        return self.processos.get(nome_programa)
   
#Classe Escalonador
class Escalonador:
    def __init__(self, quantum):
        self.quantum = quantum  # quantum do escalonador
        self.lista_prontos = [] # lista de prontos
        self.lista_bloqueados = [] # lista de bloqueados
        self.tabela_processos = TabelaProcessos() # tabela de processos
        self.contador_trocas = 0 # variável para contar as trocas feitas
        self.contador_instrucoes = 0 # variável para contar quantas instruções foram realizadas
        self.total_processos = 0 # variável para contar o número de processos carregados
        self.instrucoes_por_quantum = 0 # variável para contar instruções por quantum

    # Método para carregar os processos na tabela de processos
    def carregar_processos(self, diretorio_programas, arquivo_prioridades):
        #Carrega as prioridades dos processos de um arquivo
        prioridades = ler_prioridades(arquivo_prioridades)
        #Para cada processo, carrega o código do programa
        for i, prioridade in enumerate(prioridades):
            nome_arquivo = f"{diretorio_programas}/{i+1:02d}.txt"
            nome_processo, codigo_programa = ler_programa(nome_arquivo)
            #Cria um novo BCP e adiciona o processo na tabela e na lista de prontos
            bcp = BCP(nome_processo, prioridade, codigo_programa)
            self.adicionar_processo(bcp)
            self.total_processos += 1  # Incrementa o número total de processos
        self.lista_prontos.sort(key=lambda p: p.prioridade, reverse=True)  # Ordenar por prioridade
        for i in self.lista_prontos:
            registrar_log(f"Carregando {i.nome_programa}", self.quantum)

    # Método para adicionar processos na tabela e na lista de prontos, ordenando eles pela prioridade
    def adicionar_processo(self, bcp):
        self.tabela_processos.adicionar_processo(bcp)
        self.lista_prontos.append(bcp)
        self.lista_prontos.sort(key=lambda p: p.prioridade, reverse=True)  # Ordenar por prioridade

    # Método para executar enquanto existirem processos que não foram completados
    def executar(self):
        while self.lista_prontos or self.lista_bloqueados:
            # Verifica se todos os processos prontos têm zero crédito e redistribui se não tiverem.
            # Os créditos zeram quando cada processo esgota seus respectivos créditos. Sendo assim, há uma redistribuição dos créditos para 
            # reiniciar o ciclo de execução, Essa redistribuição de créditos garante que os processos voltem a competir de acordo com suas 
            # prioridades iniciais e o escalonamento continue de forma justa evitando que os processos de baixa prioridade sofram com falta de créditos.
            if all(bcp.creditos == 0 for bcp in self.lista_prontos):
                self.redistribuir_creditos()

            # Atualiza a lista de bloqueados se não estiver vazia
            if self.lista_bloqueados:
                self.atualizar_bloqueados()

            # Executa o próximo processo da lista de prontos, retirando ele da lista de prontos e ordenando os processos
            if self.lista_prontos:
                bcp = self.lista_prontos.pop(0)
                self.executar_processo(bcp)
                self.lista_prontos.sort(key=lambda p: p.creditos, reverse=True) #Reordena os processos prontos pela quantidade de créditos
        
        # Quando o escalonador terminar, gerar estatísticas
        self.gerar_estatisticas()

    # Método para processar uma instrução do processo
    def executar_processo(self, bcp):
        self.contador_trocas += 1  # Conta as trocas de processo
        bcp.creditos -= 1
        instrucoes_executadas = 0

        registrar_log(f"Executando {bcp.nome_programa}", self.quantum)

        # Loop para processar a instrução em relação ao número do quantum
        for _ in range(self.quantum):
            # Condição para verificar se um processo terminou
            if bcp.contador_programa >= len(bcp.codigo_programa):
                registrar_log(f"Processo {bcp.nome_programa} terminado. X={bcp.registrador_x}, Y={bcp.registrador_y}", self.quantum)
                self.tabela_processos.remover_processo(bcp.nome_programa)
                #verifica se o processo ainda está na lista de prontos e o remove!!!!!!!!!!!!!!!!!!!!!!
                if bcp in self.lista_prontos:
                    self.lista_prontos.remove(bcp)
                return  # O processo terminou, então não há mais nada a fazer

            #Processa a instrução atual do processo 
            instrucao = bcp.codigo_programa[bcp.contador_programa]
            self.processar_instrucao(bcp, instrucao)
            bcp.contador_programa += 1
            instrucoes_executadas += 1
            self.instrucoes_por_quantum += 1
            
            # Verifica se o processo foi bloqueado
            if bcp.estado == 'Bloqueado': 
                break
        
        # Se o processo não teve E/S, ele volta à fila de prontos
        if bcp.estado == 'Pronto':
            self.lista_prontos.append(bcp)  # Reinsere na lista de prontos

        self.contador_instrucoes += instrucoes_executadas
        #registra o log no momento da interrupção da linha e inclui os valores dos registradores X e Y!!!!!!!!!!!!!!!!!!!!!!!!!!!
        registrar_log(f"Interrompendo {bcp.nome_programa} após {instrucoes_executadas} instruções. X={bcp.registrador_x}, Y={bcp.registrador_y}", self.quantum) 

    # Método para atualizar a lista de bloqueados
    def atualizar_bloqueados(self):
        # Itera sobre a lista de bloqueados de trás para frente, a fim de evitar problemas ao se alterar o
        # tamanho da lista conforme ela é percorrida !!!!!!!!!!!!!!!!!!!!!!!!!!
        for i in range(len(self.lista_bloqueados) -1, -1, -1):
            bcp = self.lista_bloqueados[i]
            bcp.tempo_espera -= 1
            # verifica se o tempo de espera é terminado
            if bcp.tempo_espera <= 0:
                bcp.estado = 'Pronto'
                # remove da lista de bloqueados e adiciona na lista de prontos
                self.lista_bloqueados.pop(i)
                # Inserindo o processo de volta na fila de prontos, mantendo ordem de chegada
                self.lista_prontos.append(bcp)
    
    # Método para redistribuir os créditos dos processos
    def redistribuir_creditos(self):
        for bcp in self.lista_prontos:
            bcp.creditos = bcp.prioridade
        self.lista_prontos.sort(key=lambda p: p.creditos, reverse=True) #reordena os processos pontos pela quantidade de créditos

    # Método para gerar estatísticas e registrar os logs finais
    def gerar_estatisticas(self):
        
        #Calcula a média de trocas e de instruções por quantum
        media_trocas = self.contador_trocas / self.total_processos if self.total_processos > 0 else 0
        media_instrucoes_por_quantum = self.instrucoes_por_quantum / self.contador_trocas if self.contador_trocas > 0 else 0

        #Registra os logs e estaísticas
        registrar_log(f"MEDIA DE TROCAS: {media_trocas}", self.quantum)
        registrar_log(f"MEDIA DE INSTRUCOES POR QUANTUM: {media_instrucoes_por_quantum}", self.quantum)
        registrar_log(f"QUANTUM: {self.quantum}", self.quantum)

    # Método para processar as instruções
    def processar_instrucao(self, bcp, instrucao):
        if instrucao.startswith('X='):
            bcp.registrador_x = int(instrucao[2:])
        elif instrucao.startswith('Y='):
            bcp.registrador_y = int(instrucao[2:])
        elif instrucao == 'COM':
            pass  # Simule a execução do comando
        elif instrucao == 'E/S':
            registrar_log(f"E/S iniciada em {bcp.nome_programa}", self.quantum)
            bcp.estado = 'Bloqueado'
            bcp.tempo_espera = 2
            self.lista_bloqueados.append(bcp) # Adiciona o processo na lista de bloqueados se a instrução for um E/S
        elif instrucao == 'SAIDA':
            self.tabela_processos.remover_processo(bcp.nome_programa)  # Remove da tabela de processos
            if bcp in self.lista_prontos:
                self.lista_prontos.remove(bcp)
            if bcp in self.lista_bloqueados:
                self.lista_bloqueados.remove(bcp)

# 3 métodos para ler os arquivos necessários
def ler_prioridades(nome_arquivo): #carrega as prioridades dos processos (definindo a ordem de execução)
    prioridades = []
    with open(nome_arquivo, 'r') as f:
        for linha in f:
            prioridades.append(int(linha.strip()))
    return prioridades

def ler_quantum(nome_arquivo): #define o tempo máximo que cada processo tem para ser executado, antes de ser interrompido
    with open(nome_arquivo, 'r') as f:
        return int(f.read().strip())

def ler_programa(nome_arquivo): #carrega o código de cada processo para que o escalonador possa executar
    nome_processo = None
    codigo = []
    try: #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        with open(nome_arquivo, 'r') as f:
            linhas = f.readlines()
            nome_processo = linhas[0].strip()
            for linha in linhas[1:]:
                codigo.append(linha.strip())
    #verificações de possíveis erros relacionados aos arquivos
    except FileNotFoundError:
        # mensagem exibida caso o arquivo não seja encontrado !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        print(f"O arquivo {nome_arquivo} não foi encontrado.")   
    except IOError:
        # mensagem exibida caso haja porblemas de leitura ou escrita no arquivo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        print(f"Não foi possível ler o arquivo {nome_arquivo}.")
    except IndexError:
        # mensagem exibida caso o arquivo não tenha as linhas esperadas !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        print(f"O arquivo {nome_arquivo} não possui o formato esperado.")
    return nome_processo, codigo

#Log e Estatísticas            
import datetime

# Método para registrar os logs
def registrar_log(mensagem, quantum):
    with open(f"log{quantum:02d}.txt", 'a') as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {mensagem}\n")

# Função main para iniciar o programa
def main():

    #for i in range(1, 22):
    quantum = ler_quantum('quantum.txt')
    escalonador = Escalonador(quantum) 
    escalonador.carregar_processos('programas', 'prioridades.txt')
    escalonador.executar()

# Chame a função main
main()

