import csv
import re

def fix_csv(input_file, output_file):
    # Regex para identificar UUID (ID)
    uuid_pattern = re.compile(r'^[a-f0-9\-]{36}$')

    with open(input_file, 'r', newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Cabeçalhos (primeira linha)
        header = next(reader)
        writer.writerow(header)

        # Variável para armazenar as linhas quebradas
        row_buffer = []

        for row in reader:
            # Verificar se a primeira coluna contém um UUID válido
            if row and uuid_pattern.match(row[0]):
                # Se houver conteúdo no buffer, escrever a linha anterior corrigida
                if row_buffer:
                    writer.writerow(row_buffer)
                    row_buffer = []  # Limpar o buffer

                # Adicionar a nova linha válida no buffer
                row_buffer = row
            else:
                # Se a linha não começar com o padrão de UUID, é uma linha quebrada, então vamos concatená-la
                if row_buffer:
                    row_buffer[5] += " " + row[5]  # Concatenar o campo 'body'
                    row_buffer[6] += " " + row[6]  # Concatenar o campo 'caption'
                else:
                    row_buffer = row  # Caso não haja nada no buffer, armazenar a linha corrente

        # Escrever qualquer conteúdo restante no buffer
        if row_buffer:
            writer.writerow(row_buffer)

def main():
    csv.field_size_limit(10**6)

    caminho_arquivo_materias = '../files/globo2023/itens/itens/itens-parte1.csv'
    caminho_arquivo_materias_ajustado = '../files/globo2023/itens/itens/itens-parte1-OK.csv'

    print(f"Corrigindo o arquivo CSV '{caminho_arquivo_materias}'...")
    fix_csv(caminho_arquivo_materias, caminho_arquivo_materias_ajustado)

    caminho_arquivo_materias = '../files/globo2023/itens/itens/itens-parte2.csv'
    caminho_arquivo_materias_ajustado = '../files/globo2023/itens/itens/itens-parte2-OK.csv'

    print(f"Corrigindo o arquivo CSV '{caminho_arquivo_materias}'...")
    fix_csv(caminho_arquivo_materias, caminho_arquivo_materias_ajustado)

    caminho_arquivo_materias = '../files/globo2023/itens/itens/itens-parte3.csv'
    caminho_arquivo_materias_ajustado = '../files/globo2023/itens/itens/itens-parte3-OK.csv'

    print(f"Corrigindo o arquivo CSV '{caminho_arquivo_materias}'...")
    fix_csv(caminho_arquivo_materias, caminho_arquivo_materias_ajustado)


if __name__ == "__main__":
    main()
