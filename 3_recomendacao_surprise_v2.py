import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy
import joblib

# Carregando os dados
df_news = pd.read_pickle('df_news.pkl')
df_final = pd.read_pickle('df_final_2.pkl')

# Verificando as colunas e amostra dos dados
print(df_news.columns)
print(df_final.columns)
print(df_news.head())
print(df_final.head())  
print(df_final['userId'].head())

# Vamos filtrar apenas as colunas relevantes para o modelo de recomendação
df_acesso = df_final[['userId', 'history', 'rating', 'politica','financeira','esporte','jornalismo','entretenimento','policial']]

df_acesso = df_acesso.copy()

# Tratando tipo de dados
df_acesso['userId'] = df_acesso['userId'].astype(str)  # Garantindo que o userId seja tratado como string
df_acesso['history'] = df_acesso['history'].astype(str)  # Garantindo que a Page seja tratada como string
df_acesso['rating'] = pd.to_numeric(df_acesso['rating'], errors='coerce')  # Garantindo que a coluna rating seja numérica, com erros tratados como NaN

# Convertendo as colunas de categorias para valores binários (0 ou 1)
categorical_columns = ['politica', 'financeira', 'esporte', 'jornalismo', 'entretenimento', 'policial']
for column in categorical_columns:
    df_acesso[column] = df_acesso[column].astype(float)  # ou int, dependendo de como você tratar as categorias

# Remover valores nulos em 'rating' se existirem
df_acesso = df_acesso.dropna(subset=['rating'])

#encoder = LabelEncoder()
#df_acesso['userId'] = encoder.fit_transform(df_acesso['userId'])
#df_acesso['history'] = encoder.fit_transform(df_acesso['history'])

print(df_acesso)

# Agora, precisamos de um objeto Reader do Surprise para transformar os dados em formato adequado
reader = Reader(rating_scale=(0.1, 100))

# Criação do dataset para o Surprise
data = Dataset.load_from_df(df_acesso[['userId', 'history', 'rating']], reader)

# TREINANDO MODELO
# Dividindo os dados em treino e teste
trainset, testset = train_test_split(data, test_size=0.2)

# Criando o modelo SVD
model = SVD()

# Treinando o modelo
model.fit(trainset)

# AVALIANDO MODELO

# Fazendo previsões no conjunto de teste
predictions = model.test(testset)

# Avaliando a precisão (RMSE - Root Mean Squared Error)
accuracy.rmse(predictions)

# SALVANDO O MODELO
# Salvar o modelo treinado
joblib.dump(model, 'svd_model.pkl')  # Salvando o modelo em um arquivo
print("Modelo SVD salvo com sucesso!")

def recommend_news(user_id, top_n=5):
    recommended_news = []
    
    if user_id not in df_acesso['userId'].values:
        print(f"O userId {user_id} não existe no conjunto de dados de acessos. Recomendações padrão serão fornecidas.")
            
        # Definir as categorias para recomendar uma notícia de cada
        categorias = ['politica', 'financeira', 'esporte', 'jornalismo', 'entretenimento', 'policial']
        
        for categoria in categorias:
            # Buscando a notícia mais recente de cada categoria
            recent_news = df_news[df_news[categoria] == 1].sort_values('issued', ascending=False).head(1)
            if not recent_news.empty:
                recommended_news.append(recent_news['page'].iloc[0])
        
        return recommended_news
    
    # Listando todas as notícias que o usuário ainda não acessou
    all_pages = df_news['page'].tolist()  # Lista de todas as notícias
    accessed_pages = df_acesso[df_acesso['userId'] == user_id]['history'].tolist()  # Notícias acessadas pelo usuário
    unread_pages = list(set(all_pages) - set(accessed_pages))  # Notícias que o usuário ainda não leu

    # Gerar previsões para essas notícias que o usuário ainda não leu
    predictions = [model.predict(user_id, page) for page in unread_pages]
    
    # Ordenando as previsões por valor de 'est' (estimativa de tempo de interesse)
    predictions.sort(key=lambda x: x.est, reverse=True)
    
    # Pegando as top N notícias mais recomendadas
    top_recommendations = predictions[:top_n]
    
    # Exibindo as top N notícias recomendadas
    recommended_pages = [rec.iid for rec in top_recommendations]
    return recommended_pages

def main():
    #user_id = "f98d1132f60d46883ce49583257104d15ce723b3bbda2147c1e31ac76f0bf069"
    user_id = "1"
    top_news = recommend_news(user_id, top_n=5)

    if isinstance(top_news, str):  # Caso a resposta seja uma mensagem de erro
        print(top_news)
    else:
        print(f"As {len(top_news)} notícias mais recomendadas para o usuário {user_id}:")
        for page in top_news:
            news_details = df_news[df_news['page'] == page]
            
            print("\n ")
            print('-' * 50)
            print(f"Notícia: {news_details['title'].values[0]}")
            print(f"URL: {news_details['url'].values[0]}")
            print(f"Issued: {news_details['issued'].values[0]}")
            print(f"Modified: {news_details['modified'].values[0]}")
            print(f"Body: {news_details['body'].values[0][:50]}...")
            print(f"Notícia: {page}")

if __name__ == "__main__":
    main()
