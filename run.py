import logging
from flask import Flask, render_template, jsonify

from src.data_engine import DataEngine, DataEngineError
from src.graph_generator import (
    plot_sector_bars,
    plot_hourly_line,
    plot_period_bars,
    plot_correlation_heatmap,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("App")

app = Flask(__name__)

# ------------------------------------------------------------------
# Inicialização do motor de dados (falha rápido com mensagem clara)
# ------------------------------------------------------------------
engine: DataEngine | None = None
startup_error: str | None = None

try:
    engine = DataEngine("data/household_power_consumption.csv")
    logger.info("Motor de dados inicializado com sucesso.")
except DataEngineError as exc:
    startup_error = str(exc)
    logger.error("Falha ao inicializar o motor de dados: %s", startup_error)
except Exception as exc:
    startup_error = f"Erro inesperado na inicialização: {exc}"
    logger.exception("Erro inesperado.")


# ------------------------------------------------------------------
# Rota principal — Dashboard
# ------------------------------------------------------------------
@app.route("/")
def home():
    if startup_error or engine is None:
        return render_template("error.html", mensagem=startup_error), 500

    try:
        stats = engine.get_stats()
        sums = engine.get_sums()
        period = engine.get_period_avg()
        hourly = engine.get_hourly_avg()
        corr = engine.get_correlation_matrix()
        peaks = engine.get_top_peak_hours()

        graficos = {
            "barras":      plot_sector_bars(sums),
            "linha_hora":  plot_hourly_line(hourly),
            "periodos":    plot_period_bars(period),
            "correlacao":  plot_correlation_heatmap(corr),
        }

        return render_template(
            "index.html",
            stats=stats,
            peaks=peaks,
            graficos=graficos,
        )

    except DataEngineError as exc:
        logger.error("Erro ao processar dados: %s", exc)
        return render_template("error.html", mensagem=str(exc)), 500
    except Exception as exc:
        logger.exception("Erro inesperado na rota /")
        return render_template("error.html", mensagem="Erro interno inesperado."), 500


# ------------------------------------------------------------------
# Rota de status (health check)
# ------------------------------------------------------------------
@app.route("/status")
def status():
    if engine is None:
        return jsonify({"status": "error", "mensagem": startup_error}), 500
    stats = engine.get_stats()
    return jsonify({
        "status": "ok",
        "registros": stats["total_registros"],
        "media_kw": round(stats["media"], 4),
    })


if __name__ == "__main__":
    app.run(debug=True)
