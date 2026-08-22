# Importa a biblioteca nativa do Python para banco de dados.
# Serve para salvar as informações em um arquivo (.db) de forma permanente, sem ter que instalar nada.
import sqlite3

# Importa a função de data e hora para registrar o momento exato em que um problema foi relatado.
from datetime import datetime


def inicializar_banco():
    # Conecta ao arquivo do banco. Se o arquivo "helpdesk_lasalle.db" não existir na pasta, ele é criado na hora.
    conexao = sqlite3.connect("helpdesk_lasalle.db")
    
    # O cursor funciona como uma "caneta" para escrever e executar os comandos dentro do banco de dados.
    cursor = conexao.cursor()

    # O comando abaixo cria a tabela 'chamados' se ela ainda não existir no arquivo.
    # Serve para definir a estrutura: ID automático, local, equipamento, descrição, prioridade, status e data.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            local TEXT NOT NULL,
            equipamento TEXT NOT NULL,
            descricao TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            data_abertura TEXT NOT NULL
        )
    """)

    # Confirma e salva a criação da tabela dentro do arquivo.
    conexao.commit()
    
    # Fecha a conexão para liberar o arquivo e não gastar memória do computador.
    conexao.close()


def criar_chamado():
    print("\n--- NOVO CHAMADO DE TI ---")
    
    # O .strip() remove espaços em branco acidentais antes ou depois do texto digitado.
    local = input("• Local (ex: Lab 02, Sala 14): ").strip()
    equipamento = input("• Equipamento (ex: PC-05, Projetor): ").strip()
    descricao = input("• Descrição do problema: ").strip()
    
    # Exibe um mini menu para padronizar a resposta da prioridade.
    print("\nPrioridade: [1] Baixa | [2] Média | [3] Alta")
    opcao_prio = input("Escolha a prioridade (1-3): ").strip()

    # Dicionário simples para converter o número digitado em uma palavra.
    # Se o usuário digitar algo inválido, o .get() define a prioridade padrão como 'Média'.
    prioridades = {"1": "Baixa", "2": "Média", "3": "Alta"}
    prioridade = prioridades.get(opcao_prio, "Média")

    # Pega o dia, mês, ano, hora e minuto atuais do sistema e transforma em texto (ex: 22/08/2026 14:30).
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Abre a conexão com o banco para salvar o novo chamado.
    conexao = sqlite3.connect("helpdesk_lasalle.db")
    cursor = conexao.cursor()

    # Insere as informações digitadas dentro das colunas da tabela.
    # O uso das interrogações (?) serve por segurança para evitar erros de digitação e falhas de código SQL.
    cursor.execute("""
        INSERT INTO chamados (local, equipamento, descricao, prioridade, data_abertura)
        VALUES (?, ?, ?, ?, ?)
    """, (local, equipamento, descricao, prioridade, data_atual))

    # Salva o novo chamado e fecha o banco.
    conexao.commit()
    conexao.close()
    
    print("\n[✓] Chamado registrado com sucesso no banco de dados!")


def listar_chamados():
    conexao = sqlite3.connect("helpdesk_lasalle.db")
    cursor = conexao.cursor()

    # Busca todas as colunas de todos os chamados salvos na tabela.
    cursor.execute("SELECT id, local, equipamento, descricao, prioridade, status, data_abertura FROM chamados")
    
    # O .fetchall() traz todos os registros encontrados no banco e os transforma em uma lista do Python.
    chamados = cursor.fetchall()
    conexao.close()

    print("\n================ LISTA DE CHAMADOS ================")
    
    # Se a lista de chamados estiver vazia (sem registros no banco), avisa o usuário.
    if not chamados:
        print("Nenhum chamado pendente no momento.")
        print("==================================================")
        return

    # Passa por cada chamado retornado do banco e exibe na tela organizado.
    for c in chamados:
        # Pega a tupla do banco e atribui cada valor a uma variável separada.
        c_id, local, equipamento, descricao, prioridade, status, data = c

        print(f"ID [{c_id}] | Status: {status} | Prioridade: {prioridade}")
        print(f"Local: {local} | Equipamento: {equipamento}")
        print(f"Problema: {descricao}")
        print(f"Aberto em: {data}")
        print("-" * 50)


def concluir_chamado():
    print("\n--- FINALIZAR CHAMADO ---")
    id_str = input("Digite o ID do chamado que deseja concluir: ").strip()

    # Verifica se o que foi digitado é realmente um número antes de mandar pro banco de dados.
    if not id_str.isdigit():
        print("\n[!] Digite apenas o número do ID.")
        return

    conexao = sqlite3.connect("helpdesk_lasalle.db")
    cursor = conexao.cursor()

    # Atualiza a coluna 'status' para 'Concluído' apenas no chamado que tiver o ID informado pelo usuário.
    cursor.execute("""
        UPDATE chamados
        SET status = 'Concluído'
        WHERE id = ?
    """, (int(id_str),))

    conexao.commit()
    
    # O .rowcount conta quantas linhas no banco foram alteradas. Se for maior que 0, significa que o ID existia.
    if cursor.rowcount > 0:
        print(f"\n[✓] Chamado #{id_str} marcado como 'Concluído'!")
    else:
        print(f"\n[!] Nenhum chamado foi encontrado com o ID #{id_str}.")

    conexao.close()


def menu():
    # Garante que a tabela no banco existe logo no primeiro segundo em que o programa abre.
    inicializar_banco()

    # O 'while True' cria um loop infinito para manter o programa aberto na tela até o usuário escolher sair.
    while True:
        print("\n=== SISTEMA DE HELPDESK ESCOLAR ===")
        print("1. Cadastrar novo chamado")
        print("2. Listar chamados registrados")
        print("3. Marcar chamado como concluído")
        print("4. Sair")
        
        opcao = input("Escolha uma opção (1-4): ").strip()

        # Direciona para a função correta de acordo com a escolha do usuário.
        if opcao == "1":
            criar_chamado()
        elif opcao == "2":
            listar_chamados()
        elif opcao == "3":
            concluir_chamado()
        elif opcao == "4":
            # Quebra o loop do 'while' e encerra a execução da aplicação.
            print("\nEncerrando o sistema... Até mais!")
            break
        else:
            print("\n[!] Opção inválida! Escolha um número entre 1 e 4.")


# Essa condição verifica se o arquivo está sendo executado diretamente por você.
# Serve para evitar que o código rode sozinho caso algum dia você decida importar este arquivo dentro de outro projeto.
if __name__ == "__main__":
    menu()