import pandas as pd

class DataEngine:
    def __init__(self, path, nrows=100000):
        self.path = path
        self.nrows = nrows
        self.df = self._load_and_clean()

    def _load_and_clean(self):
        # Carrega o dataset especificando o separador e tratando tipos
        df = pd.read_csv(self.path, sep=';', low_memory=False, nrows=self.nrows)
        
        # Colunas que queremos converter para números
        cols = ['Global_active_power', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
        
        # Converte as colunas para numéricas pois todos os dados vem como strings, forçando erros a NaN
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.dropna()

    def get_stats(self):
        """Retorna estatísticas globais para os cartões do dashboard."""
        return {
            'media': self.df['Global_active_power'].mean(),
            'pico': self.df['Global_active_power'].max()
        }

    def get_sums(self):
        """Retorna a soma de consumo por setor para o gráfico."""
        return {
            'Cozinha': self.df['Sub_metering_1'].sum(),
            'Lavanderia': self.df['Sub_metering_2'].sum(),
            'Aquecimento': self.df['Sub_metering_3'].sum()
        }