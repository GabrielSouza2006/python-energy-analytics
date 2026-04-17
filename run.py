from flask import Flask, render_template
from src.data_engine import DataEngine
from src.graph_generator import plot_to_base64

app = Flask(__name__)

# Instancia o motor de dados (apontando para a pasta data/)
# Ajuste o caminho se seu arquivo estiver em outro local
engine = DataEngine('data/household_power_consumption.csv')

@app.route('/')
def home():
    # Obtém cálculos do motor
    stats = engine.get_stats()
    sums = engine.get_sums()
    
    # Gera o gráfico baseado nas somas
    grafico = plot_to_base64(list(sums.keys()), list(sums.values()))
    
    return render_template('index.html', 
                           media_web=f"{stats['media']:.2f}", 
                           pico_web=f"{stats['pico']:.2f}",
                           grafico=grafico)

if __name__ == '__main__':
    app.run(debug=True)