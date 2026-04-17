# Dashboard de Análise de Consumo Energético (Big Data) ⚡

Este projeto é uma aplicação web desenvolvida para analisar e visualizar dados massivos de consumo elétrico residencial. Utilizando o dataset "Individual Household Electric Power Consumption", a aplicação processa mais de 2 milhões de registros para extrair insights sobre o consumo por setores da casa.

## 🚀 Tecnologias Utilizadas

* **Python 3.12+**
* **Pandas**: Processamento e manipulação de Big Data.
* **Flask**: Micro-framework web para o servidor e rotas.
* **Matplotlib**: Geração de gráficos estatísticos.
* **HTML5/CSS3**: Interface do usuário e dashboard responsivo.

## 🏗️ Arquitetura do Projeto

O projeto segue uma estrutura modular para facilitar a manutenção e escalabilidade:

* `src/data_engine.py`: Motor de processamento de dados (Pandas).
* `src/graph_generator.py`: Lógica de geração de visualizações.
* `run.py`: Ponto de entrada da aplicação Flask.
* `templates/`: Interface frontend.

## 📊 O que o projeto faz?

1.  **Limpeza de Dados**: Trata valores ausentes e converte tipos de dados para análise numérica.
2.  **Cálculo de Métricas**: Calcula a média de consumo global e identifica picos de demanda energética.
3.  **Visualização por Setor**: Compara o consumo acumulado entre Cozinha, Lavanderia e Climatização através de gráficos de barras dinâmicos.

## 📂 Fonte dos Dados

O dataset utilizado foi o **Individual Household Electric Power Consumption**, disponibilizado pelo **UCI Machine Learning Repository**.

* **Link para download:** [Clique aqui para acessar o dataset](https://archive.ics.uci.edu/ml/datasets/individual+household+electric+power+consumption)
* **Descrição:** Contém 2.075.259 medições recolhidas entre dezembro de 2006 e novembro de 2010.

## 🔧 Como Rodar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/GabrielSouza2006/python-energy-analytics.git
   cd python-energy-analytics

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt

3. **Preparando os dados**
   * Baixe o dataset.
   * Extraia o arquivo .zip.
   * Mova o arquivo household_power_consumption.csv para a pasta data/ do projeto.

4. **Inicie a aplicação**
   ```bash
   python run.py