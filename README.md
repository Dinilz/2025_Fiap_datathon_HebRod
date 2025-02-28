# Sistema de Recomendação de Notícias

## Descrição

Este projeto visa desenvolver um **sistema de recomendação de notícias** baseado no histórico de consumo de usuários em um site de notícias. O objetivo é identificar padrões de leitura e prever as notícias que têm maior probabilidade de serem acessadas a seguir, utilizando técnicas de **análise de dados**, **machine learning** e **APIs**.

### Tecnologias Utilizadas
- **Python 3.9
- **Pandas**: Manipulação e análise de dados.
- **Scikit-learn**: Algoritmos de Machine Learning.
- **Surprise**: Biblioteca para recomendação.
- **FastAPI**: Criação de APIs.
- **Joblib**: Salvamento e carregamento de modelos de machine learning.
- **Tqdm**: Barra de progresso para loops.
- **CSV**: Manipulação de arquivos CSV.

## Estrutura do Projeto

- **1_fix_csv.py**: Script responsável por corrigir arquivos CSV quebrados e reorganizar os dados para processamento.
- **2_carga_ajuste_dados_v3.py**: Carrega e ajusta os dados de usuários e notícias, realizando a normalização e a classificação de categorias das notícias.
- **3_recomendacao_surprise_v2.py**: Implementa o modelo de recomendação utilizando a biblioteca **Surprise** e o algoritmo **SVD**.
- **4_API_recomendacao.py**: Cria uma API com **FastAPI** para fornecer recomendações em tempo real com base no modelo treinado.

## Pré-requisitos

Antes de rodar o projeto, é necessário configurar o ambiente. Utilize os seguintes passos:

1. **Clone o repositório**:

```bash
git clone https://github.com/Dinilz/2025_Fiap_datathon_HebRod.git
cd projeto-de-recomendacao
```

2. **Crie um ambiente virtual (opcional, mas recomendado):**:
```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
```

3. **Instale as dependências::**:
```bash
pip install -r requirements.txt
```

**Aqui estão algumas das dependências que você precisará**:
pandas
numpy
scikit-learn
surprise
fastapi
joblib
tqdm
uvicorn

## Como Utilizar

*1* - Execute o script 1_fix_csv.py para corrigir e organizar os arquivos CSV com as notícias. Ele irá corrigir eventuais erros nos arquivos e reorganizar os dados para posterior uso.
```bash
python 1_fix_csv.py
```

*2* - Execute o script 2_carga_ajuste_dados_v3.py para carregar e ajustar os dados. Ele realizará a normalização, classificação de notícias e agregação dos acessos dos usuários.
```bash
python 2_carga_ajuste_dados_v3.py
```

*3* - Execute o script 3_recomendacao_surprise_v2.py para treinar o modelo de recomendação utilizando o algoritmo SVD da biblioteca Surprise. Esse script treina o modelo de machine learning e o salva para uso posterior.
```bash
python 3_recomendacao_surprise_v2.py
```

*4* - A API de recomendação é criada com FastAPI. Para iniciar o servidor, execute o seguinte comando:
```bash
uvicorn 4_API_recomendacao:app --reload
```
