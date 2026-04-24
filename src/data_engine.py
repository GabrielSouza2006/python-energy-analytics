import logging
import os
import pandas as pd
import numpy as np

# Configuração de logging profissional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DataEngine")

# Colunas obrigatórias no dataset
REQUIRED_COLUMNS = {
    "Global_active_power",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
}

NUMERIC_COLS = list(REQUIRED_COLUMNS)


class DataEngineError(Exception):
    """Exceção customizada para erros do motor de dados."""
    pass


class DataEngine:
    """
    Motor de processamento de dados energéticos.

    Carrega, limpa e analisa o dataset UCI de consumo elétrico residencial.
    Usa dtypes explícitos e chunksize para reduzir o consumo de memória.
    """

    def __init__(self, path: str, nrows: int = 200_000):
        self.path = path
        self.nrows = nrows
        self.df: pd.DataFrame = pd.DataFrame()
        self._load_and_clean()

    # ------------------------------------------------------------------
    # Carregamento e limpeza
    # ------------------------------------------------------------------

    def _load_and_clean(self) -> None:
        """Carrega o CSV com validações completas e limpeza de dados."""
        logger.info("Iniciando carregamento do dataset: %s", self.path)

        # 1. Verificar existência do arquivo
        if not os.path.exists(self.path):
            msg = (
                f"Arquivo não encontrado: '{self.path}'. "
                "Baixe o dataset UCI e coloque-o em data/household_power_consumption.csv"
            )
            logger.error(msg)
            raise DataEngineError(msg)

        # 2. Verificar se não está vazio
        if os.path.getsize(self.path) == 0:
            msg = f"Arquivo vazio: '{self.path}'."
            logger.error(msg)
            raise DataEngineError(msg)

        # 3. Tentar carregar com dtype explícito (evita inferência cara)
        try:
            # Ler apenas as colunas necessárias reduz uso de memória
            df = pd.read_csv(
                self.path,
                sep=";",
                usecols=["Date", "Time"] + NUMERIC_COLS,
                dtype={col: "str" for col in NUMERIC_COLS},  # str -> coerce depois
                nrows=self.nrows,
                low_memory=True,
            )
        except ValueError as exc:
            # Pode ocorrer se usecols pedir colunas ausentes
            msg = f"Colunas obrigatórias ausentes no dataset. Detalhe: {exc}"
            logger.error(msg)
            raise DataEngineError(msg) from exc
        except Exception as exc:
            msg = f"Falha ao ler o CSV: {exc}"
            logger.error(msg)
            raise DataEngineError(msg) from exc

        # 4. Validar colunas presentes
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            msg = f"Colunas faltando no dataset: {missing}"
            logger.error(msg)
            raise DataEngineError(msg)

        # 5. Converter para numérico (float32 usa metade da memória do float64)
        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

        # 6. Remover linhas com NaN nas colunas críticas
        before = len(df)
        df.dropna(subset=NUMERIC_COLS, inplace=True)
        dropped = before - len(df)
        if dropped:
            logger.warning("Removidas %d linhas com valores inválidos (%.1f%%)", dropped, dropped / before * 100)

        # 7. Criar coluna datetime combinada para análises temporais
        try:
            df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True)
            df["hour"] = df["datetime"].dt.hour
            df["period"] = df["hour"].map(self._hour_to_period)
        except Exception as exc:
            logger.warning("Não foi possível parsear datas: %s. Análise temporal desativada.", exc)

        self.df = df
        logger.info("Dataset carregado com sucesso: %d registros.", len(self.df))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hour_to_period(hour: int) -> str:
        if 5 <= hour < 12:
            return "Manhã"
        elif 12 <= hour < 18:
            return "Tarde"
        elif 18 <= hour < 23:
            return "Noite"
        else:
            return "Madrugada"

    # ------------------------------------------------------------------
    # Análises
    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Estatísticas globais para os cards do dashboard."""
        if self.df.empty:
            raise DataEngineError("DataFrame vazio — não há estatísticas disponíveis.")
        col = "Global_active_power"
        return {
            "media": float(self.df[col].mean()),
            "pico": float(self.df[col].max()),
            "mediana": float(self.df[col].median()),
            "desvio": float(self.df[col].std()),
            "total_registros": len(self.df),
        }

    def get_sums(self) -> dict:
        """Soma de consumo por setor (para gráfico de barras)."""
        return {
            "Cozinha": float(self.df["Sub_metering_1"].sum()),
            "Lavanderia": float(self.df["Sub_metering_2"].sum()),
            "Climatização": float(self.df["Sub_metering_3"].sum()),
        }

    def get_hourly_avg(self) -> dict:
        """
        Consumo médio por hora do dia.
        Retorna dict {hora: média} para o gráfico de linha.
        """
        if "hour" not in self.df.columns:
            raise DataEngineError("Coluna 'hour' ausente — dados temporais não disponíveis.")

        hourly = (
            self.df.groupby("hour")["Global_active_power"]
            .mean()
            .round(4)
        )
        return hourly.to_dict()

    def get_period_avg(self) -> dict:
        """Consumo médio por período do dia (Manhã, Tarde, Noite, Madrugada)."""
        if "period" not in self.df.columns:
            raise DataEngineError("Coluna 'period' ausente.")

        order = ["Madrugada", "Manhã", "Tarde", "Noite"]
        period = (
            self.df.groupby("period")["Global_active_power"]
            .mean()
            .reindex(order)
            .round(4)
        )
        return period.to_dict()

    def get_correlation_matrix(self) -> dict:
        """
        Matriz de correlação entre as sub-medições e o consumo global.
        Retorna dict aninhado para geração do heatmap.
        """
        cols = ["Global_active_power", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]
        labels = ["Global", "Cozinha", "Lavanderia", "Climatização"]
        corr = self.df[cols].corr().round(3)
        corr.index = labels
        corr.columns = labels
        return corr.to_dict()

    def get_top_peak_hours(self, top_n: int = 5) -> list[dict]:
        """Retorna os top_n horários com maior consumo médio."""
        if "hour" not in self.df.columns:
            return []
        top = (
            self.df.groupby("hour")["Global_active_power"]
            .mean()
            .nlargest(top_n)
            .round(3)
        )
        return [{"hora": f"{int(h):02d}:00", "media_kw": v} for h, v in top.items()]
