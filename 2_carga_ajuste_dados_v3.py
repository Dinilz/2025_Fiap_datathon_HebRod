import pandas as pd
import numpy as np
import os
from datetime import datetime
from tqdm import tqdm 

caminho_arquivo_acesso_usuarios = '../files/globo2023/files/treino/treino_parte1.csv'
caminho_arquivo_materias_1 = '../files/globo2023/itens/itens/itens-parte1-OK.csv'
caminho_arquivo_materias_2 = '../files/globo2023/itens/itens/itens-parte2-OK.csv'
caminho_arquivo_materias_3 = '../files/globo2023/itens/itens/itens-parte3-OK.csv'

categorias = {
    'politica': ['presidente', 'governo', 'eleição', 'congresso', 'partido', 'político', 'Lula', 'Bolsonaro', 'governador'],
    'financeira': ['economia', 'mercado', 'investimento', 'bolsa', 'dinheiro', 'taxa de juros', 'inflação'],
    'esporte': ['futebol', 'esporte', 'jogo', 'time', 'atleta', 'campeonato', 'seleção'],
    'jornalismo': ['jornal', 'reportagem', 'notícia', 'mídia', 'imprensa', 'telejornal', 'entrevista'],
    'entretenimento': ['filme', 'série', 'música', 'celebridade', 'famoso', 'show', 'evento', 'entretenimento'],
    'policial': ['crime', 'assalto', 'roubo', 'prisão', 'assassinato', 'bandido', 'polícia', 'investigação', 'trafico', 'morto', 'mortes'],
}

def classificar_noticia(row, categorias):
    for categoria, palavras in categorias.items():
        if any(palavra in row['body'].lower() for palavra in palavras):
            row[categoria] = 1
        else:
            row[categoria] = 0
    return row

def calcular_idade_noticia(issued, data_de_hoje):
    return (data_de_hoje - issued).days

def calcular_rating(row, data_de_hoje):    

    quantidade_acessos = row['quantidade_acessos']
    media_tempo_gasto = row['tempo_medio_gasto']

    # 3. Calcular a idade da notícia
    idade_noticia = (data_de_hoje - row['modified']).days

    # Normalizar a quantidade de acessos (valores entre 0 e 1)
    max_acessos = df_news['quantidade_acessos'].max()
    acessos_normalizados = row['quantidade_acessos'] / max_acessos

    # Normalizar o tempo médio de acesso (valores entre 0 e 1)
    max_tempo = df_news['tempo_medio_gasto'].max()
    tempo_normalizado = row['tempo_medio_gasto'] / max_tempo

    peso_acessos = 0.7
    peso_tempo = 0.3

    # 4. Lógica para calcular o rating
    if quantidade_acessos == 0:
        if idade_noticia > 30:  # Notícia antiga e sem acessos
            rating = 10
        else:  # Notícia nova sem acessos
            rating = 40  # Rating intermediário para notícias novas sem acesso
    else:
        # Considerar um peso maior para o tempo na página e número de acessos
        #rating = min(100, max(1, (quantidade_acessos * 0.4) + (media_tempo_gasto * 0.3)))
        rating = (acessos_normalizados * peso_acessos + tempo_normalizado * peso_tempo) * 100

    return rating

# Recuperando data atual
#data_de_hoje = pd.Timestamp.now().normalize()
data_de_hoje = pd.Timestamp('2022-08-15').normalize()

# Leitura dos arquivos
print("LENDO OS ARQUIVOS E GERANDO DF's...")
df_users     = pd.read_csv(caminho_arquivo_acesso_usuarios)
df_news_1 = pd.read_csv(caminho_arquivo_materias_1)
df_news_2 = pd.read_csv(caminho_arquivo_materias_2)
df_news_3 = pd.read_csv(caminho_arquivo_materias_3)

# Concatenar os dataframes de notícias
df_news = pd.concat([df_news_1, df_news_2, df_news_3], ignore_index=True)

print("NORMALIZANDO O DATAFRAME DE USUARIO...")

# Separar os dados das colunas que têm múltiplos valores em listas
columns_to_split = ['history', 'timestampHistory', 'numberOfClicksHistory', 'timeOnPageHistory', 
                    'scrollPercentageHistory', 'pageVisitsCountHistory', 'timestampHistory_new']

# Transformar as listas de strings para listas reais (se necessário)
for column in columns_to_split:
    df_users[column] = df_users[column].apply(lambda x: x.split(', ') if isinstance(x, str) else x)

# Vamos criar um novo DataFrame 'explodido' para organizar melhor esses dados
df_exploded = pd.DataFrame()

# Cada linha do novo DataFrame será composta pelas listas das colunas
for column in columns_to_split:
    df_exploded[column] = df_users[column].explode()

# Agora podemos associar o 'userId' repetidamente com essas novas linhas.
df_exploded['userId'] = df_users['userId'].repeat(df_users['historySize'])
df_exploded['userType'] = df_users['userType'].repeat(df_users['historySize'])
df_exploded['historySize'] = df_users['historySize'].repeat(df_users['historySize'])

# Exibir o DataFrame final
print(df_exploded[['userId', 'historySize', 'numberOfClicksHistory']].head(10))
print(df_exploded[['userId', 'history', 'numberOfClicksHistory']].head(10))

# Tratando as colunas de data
print("TRATANDO AS COLUNAS DE DATA...")
tqdm.pandas(desc="Transformando as datas")
# Convertendo a coluna de timestampHistory para datetime no df_acesso
df_exploded['timestampHistory'] = df_exploded['timestampHistory_new'].progress_apply(lambda x: pd.to_datetime(int(x) / 1000, unit='s'))
# Convertendo as colunas de data em df_noticias
df_news['modified'] = pd.to_datetime(df_news['modified']).dt.tz_localize(None)
df_news['issued'] = pd.to_datetime(df_news['issued']).dt.tz_localize(None)

# tratando as colunas de número
df_exploded['timeOnPageHistory'] = pd.to_numeric(df_exploded['timeOnPageHistory'], errors='coerce')

# Classificando a noticia
print("CLASSIFICANDO A NOTICIA...")
tqdm.pandas(desc="Classificando as notícias")
df_news = df_news.progress_apply(classificar_noticia, axis=1, categorias=categorias)

print("ATUALIZANDO O DF_NEWS, INCLUINDO INFORMAÇÕES DE ACESSO...")
# Converte 'timeOnPageHistory' e 'pageVisitsCountHistory' para numéricos
df_exploded['timeOnPageHistory'] = pd.to_numeric(df_exploded['timeOnPageHistory'], errors='coerce')
df_exploded['pageVisitsCountHistory'] = pd.to_numeric(df_exploded['pageVisitsCountHistory'], errors='coerce')

# Calculando as métricas para cada página no df_acesso
acessos_agrupados = df_exploded.groupby('history').agg(
    quantidade_acessos=('pageVisitsCountHistory', 'sum'),  # Somando as visitas para cada página
    tempo_medio_gasto=('timeOnPageHistory', 'mean')  # Calculando a média do tempo gasto por página
).reset_index()

# Renomeando a coluna 'history' para 'page' para facilitar a junção com df_news
acessos_agrupados.rename(columns={'history': 'page'}, inplace=True)

# Agora, vamos mesclar o df_news com o df_acesso_agrupado com base na coluna 'page'
df_news = df_news.merge(acessos_agrupados, on='page', how='left')

# Substituindo valores NaN por 0 (caso não haja acesso para a notícia)
df_news['quantidade_acessos'].fillna(0, inplace=True)
df_news['tempo_medio_gasto'].fillna(0, inplace=True)

# Criando a coluna de rating
print("CRIANDO A COLUNA DE RATING NO DF_NEWS...")
tqdm.pandas(desc="Calculando o rating")
df_news['rating'] = df_news.progress_apply(lambda row: calcular_rating(row, data_de_hoje), axis=1)

print("MERGE DOS DATAFRAMES USERS e NEWS...")
df_final = pd.merge(df_exploded, df_news, how='left', left_on='history', right_on='page')
print(df_final.head())

df_final_top_100 = df_final.drop(columns=['title', 'body', 'caption']).head(100)
df_final_top_100.to_csv('resultados_final_top_100.csv', index=False)

df_news_top_100 = df_news.drop(columns=['title', 'body', 'caption']).head(100)
df_news_top_100.to_csv('resultados_news_top_100.csv', index=False)

print("SALVANDO DF FINAL...")
df_news.to_pickle('df_news.pkl')
df_final.to_pickle('df_final_2.pkl')




