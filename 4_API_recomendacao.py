from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

# Inicializando o app FastAPI
app = FastAPI(
    title="API de Recomendação",
    description="API para recomendar notícias com base no modelo de aprendizado de máquina.",
    version="1.0",
)

# Carregar o modelo salvo
model = joblib.load('svd_model.pkl')
df_news = pd.read_pickle('df_news.pkl')
df_final = pd.read_pickle('df_final_2.pkl')
df_acesso = df_final[['userId', 'history', 'rating', 'politica', 'financeira', 'esporte', 'jornalismo', 'entretenimento', 'policial']]

# Função para recomendar notícias
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

# Definir o modelo de entrada usando Pydantic
class RecommendationRequest(BaseModel):
    user_id: str
    top_n: int = 5  # Número de notícias recomendadas (default é 5)

@app.post("/recomendacao", response_model=list)
def get_recommendations(request: RecommendationRequest):
    """
    Recomendação de notícias para o usuário.
    Este endpoint recebe um 'user_id' e o número de notícias recomendadas.
    """
    # Pegando os parâmetros
    user_id = request.user_id
    top_n = request.top_n
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Parâmetro 'user_id' é necessário")

    # Chama a função de recomendação
    top_news = recommend_news(user_id, top_n)
    
    return top_news  # Retorna as recomendações como resposta JSON

if __name__ == '__main__':
    # Para rodar o app usando o uvicorn, execute no terminal: uvicorn <nome_do_arquivo>:app --reload
    pass
