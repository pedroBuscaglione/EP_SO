#Classe BCP (Bloco de Controle de Processo)
class BCP:
    def __init__(self, nome_programa, prioridade, codigo_programa):
        # O método __init__ é o construtor da classe. Ele é chamado automaticamente quando uma nova instância da classe é criada.
        
        self.contador_programa = 0
        # Inicializa o contador de programa, que indica a posição atual no código do programa. Começa em 0, indicando o início do código.

        self.estado = 'Pronto'  # Estados possíveis: 'Executando', 'Pronto', 'Bloqueado'
        # Define o estado inicial do processo como 'Pronto'. O estado pode ser 'Executando', 'Pronto', ou 'Bloqueado'.

        self.prioridade = prioridade
        # Define a prioridade do processo. A prioridade influencia a ordem em que os processos são executados.

        self.creditos = prioridade
        # Inicializa o número de créditos do processo com a mesma prioridade. Créditos são usados para determinar quanto tempo de CPU um processo tem antes de ser interrompido.

        self.registrador_x = 0
        # Inicializa o registrador X do processo com 0. O registrador X é um dos registradores de uso geral no processo.

        self.registrador_y = 0
        # Inicializa o registrador Y do processo com 0. O registrador Y é outro registrador de uso geral no processo.

        self.codigo_programa = codigo_programa
        # Define o código do programa do processo. Isso é uma lista ou outro tipo de estrutura que contém as instruções que o processo deve executar.

        self.nome_programa = nome_programa
        # Armazena o nome do programa associado a este processo. O nome é útil para identificação e gerenciamento dos processos.

        self.tempo_espera = 0  # Usado para processos bloqueados
        # Inicializa o tempo de espera do processo com 0. Esse tempo é utilizado para processos que estão bloqueados, indicando quanto tempo eles devem esperar antes de serem movidos de volta para a lista de processos prontos.

class TabelaProcessos:
    def __init__(self):
        self.processos = {} #Dicionário para armazenar BCPs com base no nome do processo 

    def adicionar_processo(self, bcp):
        self.processos[bcp.nome_programa] = bcp

    def remover_processo(self, nome_programa):
        if nome_programa in self.processos:
            del self.processos[nome_programa]

    def obter_bcp(self, nome_programa):
        return self.processos.get(nome_programa)
    
    def ler_prioridades(nome_arquivo):
    prioridades = []
    with open(nome_arquivo, 'r') as f:
        for linha in f:
            prioridades.append(int(linha.strip()))
    return prioridades

def ler_quantum(nome_arquivo):
    with open(nome_arquivo, 'r') as f:
        return int(f.read().strip())

def ler_programa(nome_arquivo):
    nome_processo = None
    codigo = []
    with open(nome_arquivo, 'r') as f:
        linhas = f.readlines()
        nome_processo = linhas[0].strip()
        for linha in linhas[1:]:
            codigo.append(linha.strip())
    return nome_processo, codigo

    
#Classe Escalonador
class Escalonador:
    def __init__(self, quantum):
        self.quantum = quantum
        self.lista_prontos = []
        self.lista_bloqueados = []
        self.tabela_processos = TabelaProcessos()

    def adicionar_processo(self, bcp):
        self.tabela_processos.adicionar_processo(bcp)
        self.lista_prontos.append(bcp)
        self.lista_prontos.sort(key=lambda p: p.prioridade, reverse=True)  # Ordenar por prioridade

    def executar(self):
        while self.lista_prontos or self.lista_bloqueados:
            if self.lista_prontos:
                bcp = self.lista_prontos.pop(0)
                self.executar_processo(bcp)
                self.lista_prontos.sort(key=lambda p: p.prioridade, reverse=True)
            if len(self.lista_bloqueados) > 0:
                self.atualizar_bloqueados()

    def executar_processo(self, bcp):
        for _ in range(self.quantum):
            if bcp.contador_programa >= len(bcp.codigo_programa):
                print(f"Processo {bcp.nome_programa} terminado.")
                self.tabela_processos.remover_processo(bcp.nome_programa)
                return
            instrucao = bcp.codigo_programa[bcp.contador_programa]
            self.processar_instrucao(bcp, instrucao)
            bcp.contador_programa += 1

    def processar_instrucao(self, bcp, instrucao):
        if instrucao.startswith('X='):
            bcp.registrador_x = int(instrucao[2:])
        elif instrucao.startswith('Y='):
            bcp.registrador_y = int(instrucao[2:])
        elif instrucao == 'COM':
            pass  # Simule a execução do comando
        elif instrucao == 'E/S':
            bcp.estado = 'Bloqueado'
            bcp.tempo_espera = 2  # Tempo de espera exemplo
            self.lista_bloqueados.append(bcp)
        elif instrucao == 'SAIDA':
            print(f"Processo {bcp.nome_programa} finalizado.")
            self.tabela_processos.remover_processo(bcp.nome_programa)

            #Log e Estatísticas
            import datetime

def registrar_log(mensagem, quantum):
    with open(f"log{quantum:02d}.txt", 'a') as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {mensagem}\n")

        #testes
        def testar_escalonador():
         escalonador = Escalonador()
         escalonador.carregar_processos('programas', 'prioridades.txt', 'quantum.txt')
         escalonador.executar()

         # Chame a função de teste
        testar_escalonador()

        
