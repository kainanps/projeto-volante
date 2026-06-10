import asyncio
import json
import websockets
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

# Inicializa os controladores
mouse = MouseController()
teclado = KeyboardController()

# Configuração da tela
LARGURA_TELA = 1920
CENTRO_X = LARGURA_TELA // 2
ALTURA_Y = 540

# Variável para controlar se já estamos apertando o pedal, evitando "spam" de teclas
estado_pedal = None 

async def processar_comando(websocket):
    global estado_pedal
    print("📱 Celular conectado com sucesso!")
    try:
        async for mensagem in websocket:
            dados = json.loads(mensagem)
            volante = dados.get('volante', 0)
            pedal = dados.get('pedal', 0)
            
            # ==========================================
            # 1. CONTROLE DA DIREÇÃO (Eixo X do Mouse)
            # ==========================================
            
            # Zona morta: Se o volante estiver entre -5 e 5 graus, o caminhão vai reto
            if abs(volante) < 5:
                volante = 0
            
            # Aumentamos o limite para 70 graus para deixar a direção menos sensível
            volante_limitado = max(-70, min(70, volante))
            
            # Regra de três considerando a nova amplitude total (140 graus)
            posicao_x = CENTRO_X + (volante_limitado * (LARGURA_TELA / 140))
            mouse.position = (posicao_x, ALTURA_Y)
            
            # ==========================================
            # 2. CONTROLE DOS PEDAIS (Teclas W e S)
            # ==========================================
            
            # Se inclinar mais de 15 graus para um lado, acelera
            if pedal > 15:
                if estado_pedal != 'frente':
                    teclado.release('s')
                    teclado.press('w')
                    estado_pedal = 'frente'
                    
            # Se inclinar mais de 15 graus para o outro, freia/ré
            elif pedal < -15:
                if estado_pedal != 're':
                    teclado.release('w')
                    teclado.press('s')
                    estado_pedal = 're'
                    
            # Se estiver na zona neutra da inclinação frontal, solta os pedais
            # Se estiver na zona neutra da inclinação frontal, solta os pedais
            else:
                if estado_pedal is not None:
                    teclado.release('w')
                    teclado.release('s')
                    estado_pedal = None
            
    except websockets.exceptions.ConnectionClosed:
        print("Celular desconectado.")
        # Solta as teclas caso a conexão caia
        teclado.release('w')
        teclado.release('s')
        estado_pedal = None

async def main():
    async with websockets.serve(processar_comando, "0.0.0.0", 8080):
        print("🚀 Servidor rodando! Aguardando conexão do celular...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())