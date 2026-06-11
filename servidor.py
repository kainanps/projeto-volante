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

estado_pedal = 'neutro'

async def processar_comando(websocket):
    global estado_pedal
    print("📱 Celular conectado com sucesso!")
    try:
        async for mensagem in websocket:
            dados = json.loads(mensagem)
            volante = dados.get('volante', 0)
            pedal = dados.get('pedal', 'neutro')
            
            # ==========================================
            # 1. CONTROLE DA DIREÇÃO (Eixo X do Mouse)
            # ==========================================
            if abs(volante) < 5:
                volante = 0
            
            volante_limitado = max(-70, min(70, volante))
            posicao_x = CENTRO_X + (volante_limitado * (LARGURA_TELA / 140))
            mouse.position = (posicao_x, ALTURA_Y)
            
            # ==========================================
            # 2. CONTROLE DOS PEDAIS (Botões da Tela)
            # ==========================================
            if pedal == 'frente':
                if estado_pedal != 'frente':
                    teclado.release('s')
                    teclado.press('w')
                    estado_pedal = 'frente'
                    
            elif pedal == 're':
                if estado_pedal != 're':
                    teclado.release('w')
                    teclado.press('s')
                    estado_pedal = 're'
                    
            else: # neutro
                if estado_pedal != 'neutro':
                    teclado.release('w')
                    teclado.release('s')
                    estado_pedal = 'neutro'
            
    except websockets.exceptions.ConnectionClosed:
        print("Celular desconectado.")
        teclado.release('w')
        teclado.release('s')
        estado_pedal = 'neutro'

async def main():
    async with websockets.serve(processar_comando, "0.0.0.0", 8080):
        print("🚀 Servidor rodando! Aguardando conexão do celular...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())