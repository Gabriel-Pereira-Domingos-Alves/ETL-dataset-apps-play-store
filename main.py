import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os

class ETLProcess:
    def __init__(self, input_df, output_df, db_path):
        self.input_df = input_df
        self.output_df = output_df
        self.db_path = db_path
        self.data = None

    def extract(self):
        self.data = pd.read_csv(self.input_df)
    
    def cleanData(self):
        self.data = self.data.dropna()
        self.data = self.data.drop_duplicates()
        self.data = self.data.drop(['Android Ver', 'Current Ver', 'Price', 'Size', 'Last Updated'], axis=1)
        self.data['Installs'] = self.data['Installs'].replace(r'[+,]', '', regex=True)
        self.data['Installs'] = pd.to_numeric(self.data['Installs'])
        self.data['Category'] = self.data['Category'].str.lower()
        self.data['Reviews'] = pd.to_numeric(self.data['Reviews'], errors='coerce')  # Converter para numérico
        self.data['Rating'] = pd.to_numeric(self.data['Rating'], errors='coerce')  # Converter para numérico
        self.data = self.data.dropna(subset=['Reviews', 'Rating'])
    
    def transform(self):
        self.data.to_csv(self.output_df, index=False)

    def save_to_db(self):
        # Se houver um diretório no caminho do banco de dados, cria-o
        dir_name = os.path.dirname(self.db_path)
        if dir_name:  # Verifica se o caminho inclui um diretório
            os.makedirs(dir_name, exist_ok=True)
        
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect(self.db_path)
        # Salvar o DataFrame no banco de dados
        self.data.to_sql('google_play_apps', conn, if_exists='replace', index=False)
        # Fechar a conexão
        conn.close()

    def calculate_weighted_score(self):
        # Calcular o total de reviews
        total_reviews = self.data['Reviews'].sum()
        # Calcular a pontuação ponderada
        self.data['Weighted Score'] = (self.data['Rating'] * self.data['Reviews']) / total_reviews

    def visualizeData(self):
        plt.figure(figsize=(20, 8))
        sns.countplot(y='Category', data=self.data, order=self.data['Category'].value_counts().index)
        plt.title('Contagem de Aplicativos por Categoria')
        plt.xlabel('Número de Aplicativos')
        plt.ylabel('Categoria')
        plt.savefig('category_count.png')

        df_sorted = self.data.sort_values(['Category', 'Installs'], ascending=[True, False])
        top_df = df_sorted.groupby('Category').head(1)
        plt.figure(figsize=(32, 14))
        sns.barplot(x='Installs', y='App', hue='Category', data=top_df, dodge=False)
        plt.title('Top Aplicativos com Mais Instalações em Cada Categoria')
        plt.xlabel('Número de Instalações')
        plt.ylabel('Nome do Aplicativo')
        plt.legend(title='Categoria', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.savefig('top-apps-category.png')
        
        self.calculate_weighted_score()
        # Salvar o gráfico dos 10 aplicativos com maior pontuação ponderada
        top_weighted_df = self.data.sort_values(by='Weighted Score', ascending=False).head(23)
        plt.figure(figsize=(32, 15))
        sns.barplot(x='Weighted Score', y='App', data=top_weighted_df, palette='viridis')
        plt.title('Top 10 Aplicativos com Maior Pontuação Ponderada')
        plt.xlabel('Pontuação Ponderada')
        plt.ylabel('Nome do Aplicativo')
        plt.savefig('top_10_weighted_score.png')  # Salvar o gráfico como um arquivo PNG
        plt.close()  # Fechar a figura para liberar memória

if __name__ == "__main__":
    input_df = "datasets/googleplaystore.csv"
    output_df = "datasets/googleplaystore_clean.csv"
    db_path='etl_database.db'
    
    etl = ETLProcess(input_df, output_df, db_path)
    etl.extract()
    etl.cleanData()
    etl.save_to_db()
    etl.transform()
    etl.visualizeData()