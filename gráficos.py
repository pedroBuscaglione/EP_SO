import os
import re
import matplotlib.pyplot as plt

# Função para extrair as médias de trocas e instruções de um arquivo log
def extrair_dados_log(quantum):
    nome_arquivo = f"log{quantum:02d}.txt"
    media_trocas = None
    media_instrucoes = None

    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r') as arquivo:
            for linha in arquivo:
                if 'MEDIA DE TROCAS' in linha:
                    media_trocas = float(re.search(r'(\d+\.\d+)', linha).group(1))
                elif 'MEDIA DE INSTRUCOES POR QUANTUM' in linha:
                    media_instrucoes = float(re.search(r'(\d+\.\d+)', linha).group(1))
    return media_trocas, media_instrucoes

# Função para calcular a métrica de otimização
def calcular_otimizacao(trocas, instrucoes):
    if trocas == 0:
        return 0
    return instrucoes / trocas  # Otimização = Instruções / Trocas (maior é melhor)

# Listas para armazenar os dados
quantum_values = list(range(1, 22))  # Quantum de 1 até 21
media_trocas = []
media_instrucoes = []
metricas_otimizacao = []

# Extrai os dados dos arquivos de log e calcula a métrica de otimização
for quantum in quantum_values:
    trocas, instrucoes = extrair_dados_log(quantum)
    if trocas is not None and instrucoes is not None:
        media_trocas.append(trocas)
        media_instrucoes.append(instrucoes)
        metricas_otimizacao.append(calcular_otimizacao(trocas, instrucoes))
    else:
        # Caso não consiga ler o arquivo, insere um valor padrão (ex.: 0)
        media_trocas.append(0)
        media_instrucoes.append(0)
        metricas_otimizacao.append(0)

# Identificar o quantum com a melhor métrica de otimização
quantum_ideal = quantum_values[metricas_otimizacao.index(max(metricas_otimizacao))]
print(f"O quantum mais otimizado é: {quantum_ideal}")

# Plotar os gráficos de Trocas, Instruções e Otimização
plt.figure(figsize=(12, 8))

# Gráfico da média de trocas
plt.subplot(2, 1, 1)
plt.plot(quantum_values, media_trocas, marker='o', color='b', label='Média de Trocas')
plt.title('Média de Trocas e Instruções por Quantum')
plt.ylabel('Média de Trocas')
plt.grid(True)

# Gráfico da média de instruções
plt.subplot(2, 1, 2)
plt.plot(quantum_values, media_instrucoes, marker='o', color='g', label='Média de Instruções')
plt.axvline(x=quantum_ideal, color='r', linestyle='--', label=f'Quantum Otimizado: {quantum_ideal}')
plt.xlabel('Quantum')
plt.ylabel('Média de Instruções por Quantum')
plt.grid(True)

plt.tight_layout()
plt.show()

# Plotar a métrica de otimização para visualização
plt.figure(figsize=(10, 6))
plt.plot(quantum_values, metricas_otimizacao, marker='o', color='r', label='Métrica de Otimização (Instruções/Trocas)')
plt.axvline(x=quantum_ideal, color='b', linestyle='--', label=f'Quantum Otimizado: {quantum_ideal}')
plt.title('Métrica de Otimização por Quantum')
plt.xlabel('Quantum')
plt.ylabel('Otimização (Instruções / Trocas)')
plt.grid(True)
plt.legend()
plt.show()
