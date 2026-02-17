#===================#
# Intv-TestBox      #
# 2025 - MasterMIB  #
# V1.0              #
#===================#
# Adafruit CircuitPython 9.2.1 on 2024-11-20; Raspberry Pi Pico with rp2040

import board
import busio
import digitalio
import adafruit_ssd1306
import adafruit_framebuf
import time
import random

# Configuração do Display OLED I2C
# GP13 = SCL
# GP12 = SDA
i2c = busio.I2C(board.GP13, board.GP12)  # (SCL, SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Definição dos pinos do DB9 no RP2040
# DB9 macho visto de frente para o conector
#  1 2 3 4 5
#   6 7 8 9
# GP0 = 1
# GP1 = 2
# GP2 = 3
# GP3 = 4
# GP4 = 5
# GP5 = 6
# GP6 = 7
# GP7 = 8
# GP8 = 9
db9_pins = [
    board.GP0, board.GP1, board.GP2, board.GP3, board.GP4,
    board.GP5, board.GP6, board.GP7, board.GP8
]

# Criar lista de objetos DigitalInOut
pin_objects = [digitalio.DigitalInOut(pin) for pin in db9_pins]

# Coordenadas dos pinos no display OLED (deslocados para baixo)
pin_positions = {
    1: (30, 26), 2: (50, 26), 3: (70, 26), 4: (90, 26), 5: (110, 26),    
    6: (40, 48), 7: (60, 48), 8: (80, 48), 9: (100, 48)
}

# Tabela de combinações de pinos
combinacoesDB = {
    #número/PinosDB: 1 2 3 4 5 6 7 8 9
    "D1": [1, 0, 0, 1, 0, 0, 0, 0, 0],
    "D2": [1, 0, 0, 1, 0, 1, 0, 0, 0],
    "D3": [1, 0, 1, 1, 0, 1, 0, 0, 0],
    "D4": [1, 0, 1, 1, 0, 0, 0, 0, 0],
    "D5": [1, 0, 1, 0, 0, 0, 0, 0, 0],
    "D6": [1, 0, 1, 0, 0, 1, 0, 0, 0],
    "D7": [1, 1, 1, 0, 0, 1, 0, 0, 0],
    "D8": [1, 1, 1, 0, 0, 0, 0, 0, 0],
    "D9": [1, 1, 0, 0, 0, 0, 0, 0, 0],
    "D10": [1, 1, 0, 0, 0, 1, 0, 0, 0],
    "D11": [1, 1, 0, 0, 1, 1, 0, 0, 0],
    "D12": [1, 1, 0, 0, 1, 0, 0, 0, 0],
    "D13": [1, 0, 0, 0, 1, 0, 0, 0, 0],
    "D14": [1, 0, 0, 0, 1, 1, 0, 0, 0],
    "D15": [1, 0, 0, 1, 1, 1, 0, 0, 0],
    "D16": [1, 0, 0, 1, 1, 0, 0, 0, 0],
    "T0": [1, 0, 0, 0, 1, 0, 0, 1, 0],
    "T1": [1, 1, 0, 0, 0, 0, 0, 0, 1],
    "T2": [1, 1, 0, 0, 0, 0, 0, 1, 0],
    "T3": [1, 1, 0, 0, 0, 0, 1, 0, 0],
    "T4": [1, 0, 1, 0, 0, 0, 0, 0, 1],
    "T5": [1, 0, 1, 0, 0, 0, 0, 1, 0],
    "T6": [1, 0, 1, 0, 0, 0, 1, 0, 0],
    "T7": [1, 0, 0, 1, 0, 0, 0, 0, 1],
    "T8": [1, 0, 0, 1, 0, 0, 0, 1, 0],
    "T9": [1, 0, 0, 1, 0, 0, 1, 0, 0],
    "TC": [1, 0, 0, 0, 1, 0, 0, 0, 1],
    "TE": [1, 0, 0, 0, 1, 0, 1, 0, 0],
    "B1": [1, 0, 0, 0, 0, 0, 1, 0, 1],
    "B2": [1, 0, 0, 0, 0, 0, 1, 1, 0],
    "B3": [1, 0, 0, 0, 0, 0, 0, 1, 1],
    "BP": [1, 1, 0, 1, 0, 0, 1, 0, 1]
}

def detectar_combinacao(estado_pinos):
    d, t, b = "D--", "T--", "B--"
    for nome, combinacao in combinacoesDB.items():
        if combinacao == estado_pinos:
            if nome.startswith("D"): d = nome
            elif nome.startswith("T"): t = nome
            elif nome.startswith("B"): b = nome
    return f"{d}   {t}   {b}"

def detect_shorts():
    connections = []
    detected_pins = set()
    estado_pinos = [0] * 9
    for i in range(len(pin_objects)):
        for pin in pin_objects:
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.UP
        pin_objects[i].direction = digitalio.Direction.OUTPUT
        pin_objects[i].value = False
        for j in range(len(pin_objects)):
            if i != j and not pin_objects[j].value:
                if (j + 1, i + 1) not in connections:
                    connections.append((i + 1, j + 1))
                detected_pins.add(i + 1)
                detected_pins.add(j + 1)
                estado_pinos[j] = 1
    return connections, detected_pins, estado_pinos

def draw_filled_circle(oled, x, y, r, color):
    for i in range(-r, r):
        for j in range(-r, r):
            if i**2 + j**2 <= r**2:
                oled.pixel(x + i, y + j, color)
      
def draw_layout(connections, detected_pins, estado_pinos):
    oled.fill(0)
    
    oled.text("I2-macho frente conexão", 1, 57, 1)
    
    combinacao = detectar_combinacao(estado_pinos)
    oled.text(combinacao, 25, 0, 1)
    for pino, (x, y) in pin_positions.items():
        if pino in detected_pins:
            draw_filled_circle(oled, x, y, 7, 1)
            oled.text(str(pino), x - 3, y - 3, 0)  # Número em branco
        else:
            oled.circle(x, y, 7, 1)
            oled.text(str(pino), x - 3, y - 3, 1)  # Número em preto
    drawn_connections = set()
    for p1, p2 in connections:
        if (p2, p1) in drawn_connections:
            continue
        drawn_connections.add((p1, p2))
        x1, y1 = pin_positions[p1]
        x2, y2 = pin_positions[p2]
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        if y1 == y2:
            mid_y -= 10
        else:
            mid_x += 10 if x1 < x2 else -10
        oled.line(x1, y1, mid_x, mid_y, 1)
        oled.line(mid_x, mid_y, x2, y2, 1)
    oled.show()   

for _ in range(6):
    oled.text("TestBox - MasterMIB", 7, 0, 1) #C / L / ?
    oled.text("===================", 7, 10, 1)
    numeros = [random.randint(0, 1) for _ in range(19)]
    string_aleatoria = ''.join(map(str, numeros))
    oled.text(string_aleatoria, 7, 20, 1)
    numeros = [random.randint(0, 1) for _ in range(19)]
    string_aleatoria = ''.join(map(str, numeros))
    oled.text(string_aleatoria, 7, 30, 1)
    numeros = [random.randint(0, 1) for _ in range(19)]
    string_aleatoria = ''.join(map(str, numeros))
    oled.text(string_aleatoria, 7, 40, 1)
    numeros = [random.randint(0, 1) for _ in range(19)]
    string_aleatoria = ''.join(map(str, numeros))
    oled.text(string_aleatoria, 7, 50, 1)
    oled.show()
    #time.sleep(0.02)
    oled.fill(0)
    
time.sleep(1.50)

while True:
    conexoes, pinos_detectados, estado_pinos = detect_shorts()
    draw_layout(conexoes, pinos_detectados, estado_pinos)
    time.sleep(0.05)