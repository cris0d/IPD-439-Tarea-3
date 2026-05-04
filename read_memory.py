import serial
import time

# Configuración
PORT = 'COM4'        
BAUDRATE = 115200
ADDRESS = 0x08000000
NUM_BYTES = 256      # bytes a leer

ACK = b'\x79'
NACK = b'\x1F'

def xor_checksum(data):
    checksum = 0
    for b in data:
        checksum ^= b
    return checksum

def wait_ack(ser, step=""):
    resp = ser.read(1)
    if resp == ACK:
        print(f"[OK] ACK ({step})")
        return True
    raise Exception(f"[ERROR] {resp} ({step})")

ser = serial.Serial(
    PORT,
    BAUDRATE,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2
)

time.sleep(0.5)

# Sincronizar
print("Sincronizando...")
ser.write(b'\x7F')
wait_ack(ser, "SYNC")

# Read Memory
print("Enviando comando READ MEMORY...")
cmd = bytes([0x11, 0xEE])  # complemento
ser.write(cmd)
wait_ack(ser, "CMD")

# Direccion de inicio
addr_bytes = ADDRESS.to_bytes(4, 'big')
checksum = xor_checksum(addr_bytes)
ser.write(addr_bytes + bytes([checksum]))
wait_ack(ser, "ADDRESS")

# Tamaño a leer
N = NUM_BYTES - 1
size_byte = N & 0xFF
checksum = size_byte ^ 0xFF

ser.write(bytes([size_byte, checksum]))
wait_ack(ser, "SIZE")

# Leer datos
data = ser.read(NUM_BYTES)

print("\nDatos leídos:")
for i in range(0, len(data), 16):
    chunk = data[i:i+16]
    print(f"{ADDRESS + i:08X} : " + " ".join(f"{b:02X}" for b in chunk))

ser.close()
print("\nLectura completada.")

# Exportar datos a .bin
with open("mem_stm32.bin", "wb") as f:
    f.write(data)