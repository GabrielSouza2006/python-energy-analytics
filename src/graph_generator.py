import matplotlib.pyplot as plt
import io
import base64

def plot_to_base64(nomes, valores):
    """Gera um gráfico e converte para string base64 para o HTML."""
    plt.figure(figsize=(8, 5))
    cores = ['#3498db', '#2ecc71', '#e74c3c']
    
    plt.bar(nomes, valores, color=cores)
    plt.title('Consumo Acumulado por Setor (Watt-hora)')
    plt.ylabel('Consumo Total')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Salva o gráfico em memória
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    
    # Converte para base64
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return plot_url