from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)


# Variável global para armazenar o último valor de nível de água
ultimo_nivel_agua = None

# Endpoint raiz
@app.route('/')
def home():
    return "<h1>Bem-vindo à API de Monitoramento de Nível de Água</h1><p>Use o endpoint /enviar_nivel_agua para enviar o nível de água.</p>"

# Endpoint para receber o nível de água
@app.route('/enviar_nivel_agua', methods=['POST'])
def enviar_nivel_agua():
    global ultimo_nivel_agua
    try:
        # Recebe o nível de água em porcentagem enviado na requisição
        data = request.json
        nivel_agua = data.get('nivel_agua')
        
        # Verifica se o nível de água é válido (de 0 a 100%)
        if nivel_agua is None or not (0 <= nivel_agua <= 100):
            return jsonify({'erro': 'Nível de água inválido. Deve ser um valor entre 0 e 100%.'}), 400
        
        # Armazena o valor do nível de água
        ultimo_nivel_agua = nivel_agua
        
        return jsonify({'mensagem': 'Nível de água recebido com sucesso', 'nivel_agua': nivel_agua}), 200

    except Exception as e:
        return jsonify({'erro': 'Erro interno no servidor', 'detalhes': str(e)}), 500

# Endpoint para exibir o status do nível de água
@app.route('/status_nivel')
def status_nivel():
    # Página HTML com gráfico usando Chart.js e atualização automática
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Status do Nível de Água</title>
        <style>
            body {
                background-color: #000000;
                color: #FFFFFF;
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 50px;
            }
            h1 {
                font-size: 2em;
                color: #00BFFF;
                margin-bottom: 30px;
            }
            #gauge {
                width: 300px;
                height: 300px;
                margin: auto;
            }
            #status_text {
                font-size: 1.5em;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Bem-vindo à Caixa d'Água Inteligente</h1>
        <canvas id="gauge"></canvas>
        <p id="status_text"></p>
        
        <!-- Incluindo Chart.js -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Função para atualizar o gráfico e o texto de nível de água
            function atualizarNivelAgua() {
                fetch('/obter_nivel_agua')
                    .then(response => response.json())
                    .then(data => {
                        const nivelAgua = data.nivel_agua;
                        document.getElementById("status_text").innerText = nivelAgua + "% do nível de água";

                        // Atualiza a cor da barra com base no nível de água
                        var corBarra = nivelAgua <= 20 || nivelAgua >= 90 ? '#FF4500' : '#32CD32';

                        // Atualiza o gráfico de gauge
                        gaugeChart.data.datasets[0].data = [nivelAgua, 100 - nivelAgua];
                        gaugeChart.data.datasets[0].backgroundColor = [corBarra, '#D3D3D3'];
                        gaugeChart.update();
                    })
                    .catch(error => console.error("Erro ao obter o nível de água:", error));
            }

            // Inicialização do gráfico de gauge
            var ctx = document.getElementById('gauge').getContext('2d');
            var gaugeChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: ['#32CD32', '#D3D3D3'],
                        borderWidth: 0
                    }]
                },
                options: {
                    circumference: 180,
                    rotation: 270,
                    cutout: '70%',
                    responsive: true,
                    plugins: {
                        tooltip: { enabled: false }
                    }
                }
            });

            // Atualiza o nível de água a cada 5 segundos
            setInterval(atualizarNivelAgua, 5000);

            // Chama a função para atualizar o nível de água imediatamente ao carregar a página
            atualizarNivelAgua();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, nivel_agua=ultimo_nivel_agua)

# Novo endpoint para obter o último nível de água
@app.route('/obter_nivel_agua', methods=['GET'])
def obter_nivel_agua():
    global ultimo_nivel_agua
    return jsonify({'nivel_agua': ultimo_nivel_agua if ultimo_nivel_agua is not None else 0})

if __name__ == '__main__':
    app.run(debug=True)


    