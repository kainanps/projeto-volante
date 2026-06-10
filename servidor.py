import asyncio
import json
import websockets
from pynput.mouse import Controller

# Inicializa o controlador do mouse
mouse = Controller()

# Configuração da tela (Ajuste para a resolução do seu monitor principal)
LARGURA_TELA = 1920
CENTRO_X = LARGURA_TELA // 2
ALTURA_Y = 540 # Meio da tela no eixo Y

async def processar_comando(websocket):
    print("📱 Celular conectado com sucesso!")
    try:
        async for mensagem in websocket:
            dados = json.loads(mensagem)
            angulo = dados.get('angulo', 0)
            
            # Limita o ângulo entre -45 (esquerda) e 45 (direita) para não bugar
            angulo_limitado = max(-45, min(45, angulo))
            
            # Converte o ângulo (-45 a 45) para a posição X da tela (0 a LARGURA_TELA)
            # Regra de três simples para mapear a inclinação para a tela
            posicao_x = CENTRO_X + (angulo_limitado * (LARGURA_TELA / 90))
            
            # Move o mouse instantaneamente
            mouse.position = (posicao_x, ALTURA_Y)
            
    except websockets.exceptions.ConnectionClosed:
        print("Celular desconectado.")

async def main():
    # O servidor vai rodar na porta 8080 em todas as interfaces de rede do PC
    async with websockets.serve(processar_comando, "0.0.0.0", 8080):
        print("🚀 Servidor rodando! Aguardando conexão do celular...")
        print("Certifique-se de colocar o IP deste computador no arquivo HTML do celular.")
        await asyncio.Future()  # Roda para sempre

if __name__ == "__main__":
    asyncio.run(main())