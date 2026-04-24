import io
import base64
import logging
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap

matplotlib.use("Agg")  # Backend sem GUI (essencial para servidores Flask)

logger = logging.getLogger("GraphGenerator")

# ------------------------------------------------------------------
# Paleta corporativa sóbria
# ------------------------------------------------------------------
PALETTE = {
    "bg":       "#0F1117",   # fundo dos gráficos
    "surface":  "#1A1D27",   # área do plot
    "grid":     "#2A2D3A",   # linhas de grade
    "text":     "#E0E4F0",   # texto principal
    "muted":    "#6B7080",   # texto secundário
    "accent1":  "#4A9EFF",   # azul elétrico
    "accent2":  "#00D4AA",   # verde-água
    "accent3":  "#FF6B6B",   # vermelho coral
    "accent4":  "#FFB347",   # âmbar
    "positive": "#00D4AA",
    "negative": "#FF6B6B",
}

SECTOR_COLORS = [PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"]]
PERIOD_COLORS = [PALETTE["accent4"], PALETTE["accent1"], PALETTE["accent3"], PALETTE["accent2"]]


def _apply_base_style(ax: plt.Axes, fig: plt.Figure) -> None:
    """Aplica o estilo corporativo padrão a qualquer eixo."""
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["surface"])
    ax.tick_params(colors=PALETTE["muted"], labelsize=9)
    ax.xaxis.label.set_color(PALETTE["text"])
    ax.yaxis.label.set_color(PALETTE["text"])
    ax.title.set_color(PALETTE["text"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["grid"])
    ax.grid(axis="y", color=PALETTE["grid"], linestyle="--", linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)


def _to_base64(fig: plt.Figure) -> str:
    """Converte figura Matplotlib para string base64."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120, facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    return encoded


# ------------------------------------------------------------------
# Gráfico 1 — Barras: Consumo acumulado por setor
# ------------------------------------------------------------------
def plot_sector_bars(sums: dict) -> str:
    """Gráfico de barras com consumo acumulado por setor (Wh)."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    _apply_base_style(ax, fig)

    names = list(sums.keys())
    values = list(sums.values())

    bars = ax.bar(names, values, color=SECTOR_COLORS, width=0.5, zorder=3)

    # Rótulos de valor sobre cada barra
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.02,
            f"{val:,.0f} Wh",
            ha="center", va="bottom",
            color=PALETTE["text"], fontsize=9, fontweight="bold",
        )

    ax.set_title("Consumo Acumulado por Setor", fontsize=13, fontweight="bold", pad=16)
    ax.set_ylabel("Energia Total (Wh)", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.tick_params(axis="x", colors=PALETTE["text"], labelsize=11)
    fig.tight_layout()
    return _to_base64(fig)


# ------------------------------------------------------------------
# Gráfico 2 — Linha: Consumo médio por hora
# ------------------------------------------------------------------
def plot_hourly_line(hourly: dict) -> str:
    """Gráfico de linha com consumo médio por hora do dia (0–23h)."""
    fig, ax = plt.subplots(figsize=(9, 4))
    _apply_base_style(ax, fig)

    hours = list(hourly.keys())
    values = list(hourly.values())

    ax.plot(hours, values, color=PALETTE["accent1"], linewidth=2, zorder=3)
    ax.fill_between(hours, values, alpha=0.15, color=PALETTE["accent1"], zorder=2)

    # Destaque do pico
    peak_hour = hours[int(np.argmax(values))]
    peak_val = max(values)
    ax.scatter([peak_hour], [peak_val], color=PALETTE["accent4"], s=80, zorder=5)
    ax.annotate(
        f"  Pico: {peak_val:.2f} kW\n  {peak_hour:02d}:00h",
        xy=(peak_hour, peak_val),
        color=PALETTE["accent4"], fontsize=8.5,
        xytext=(peak_hour + 1, peak_val),
    )

    ax.set_title("Consumo Médio por Hora do Dia", fontsize=13, fontweight="bold", pad=16)
    ax.set_xlabel("Hora", fontsize=10)
    ax.set_ylabel("kW médio", fontsize=10)
    ax.set_xticks(range(0, 24))
    ax.set_xticklabels([f"{h:02d}h" for h in range(24)], rotation=45, fontsize=7.5)
    ax.grid(axis="x", color=PALETTE["grid"], linestyle=":", linewidth=0.5, alpha=0.6)
    fig.tight_layout()
    return _to_base64(fig)


# ------------------------------------------------------------------
# Gráfico 3 — Barras horizontais: Consumo por período do dia
# ------------------------------------------------------------------
def plot_period_bars(period: dict) -> str:
    """Barras horizontais de consumo médio por período (Manhã, Tarde, Noite, Madrugada)."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    _apply_base_style(ax, fig)

    periods = list(period.keys())
    values = list(period.values())

    bars = ax.barh(periods, values, color=PERIOD_COLORS, height=0.5, zorder=3)

    for bar, val in zip(bars, values):
        ax.text(
            val + max(values) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f} kW",
            va="center", ha="left",
            color=PALETTE["text"], fontsize=9,
        )

    ax.set_title("Consumo Médio por Período do Dia", fontsize=13, fontweight="bold", pad=16)
    ax.set_xlabel("kW médio", fontsize=10)
    ax.tick_params(axis="y", colors=PALETTE["text"], labelsize=10)
    ax.grid(axis="x", color=PALETTE["grid"], linestyle="--", linewidth=0.6, alpha=0.8)
    ax.invert_yaxis()
    fig.tight_layout()
    return _to_base64(fig)


# ------------------------------------------------------------------
# Gráfico 4 — Heatmap: Correlação entre sub-medições
# ------------------------------------------------------------------
def plot_correlation_heatmap(corr_dict: dict) -> str:
    """Heatmap de correlação entre consumo global e sub-medições."""
    labels = list(corr_dict.keys())
    matrix = np.array([[corr_dict[r][c] for c in labels] for r in labels])

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    # Colormap customizado: vermelho -> cinza -> azul
    cmap = LinearSegmentedColormap.from_list(
        "corp", [PALETTE["accent3"], PALETTE["surface"], PALETTE["accent1"]]
    )
    im = ax.imshow(matrix, cmap=cmap, vmin=-1, vmax=1, aspect="auto")

    # Rótulos dos eixos
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, color=PALETTE["text"], fontsize=9, rotation=30, ha="right")
    ax.set_yticklabels(labels, color=PALETTE["text"], fontsize=9)

    # Valores dentro das células
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = matrix[i, j]
            color = PALETTE["bg"] if abs(val) > 0.5 else PALETTE["text"]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=9.5,
                    color=color, fontweight="bold")

    # Barra de cor
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=PALETTE["muted"], labelsize=8)
    cbar.outline.set_edgecolor(PALETTE["grid"])

    # Bordas das células
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["grid"])

    ax.set_title("Correlação entre Medições", fontsize=13, fontweight="bold",
                 pad=14, color=PALETTE["text"])
    fig.tight_layout()
    return _to_base64(fig)
