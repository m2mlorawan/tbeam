from cayennelpp import CayenneLPP
#from machine import Pin, I2C
from micropyGPS import MicropyGPS 
import utime, time
from ulora import TTN, uLoRa
import machine
#heltec Tbeam


#TBEAM 
LORA_CS = const(18)
LORA_SCK = const(5)
LORA_MOSI = const(27)
LORA_MISO = const(19)
LORA_IRQ = const(23)
LORA_RST = const(26)

LORA_DATARATE = "SF12BW125"  # Choose from several available
DEVADDR = bytearray([0x26, 0x01, 0x15, 0xBB])
NWKEY = bytearray([0xA6, 0xC3, 0x0F, 0xB2, 0x91, 0xDB, 0x55, 0xC5,
                   0x31, 0x82, 0x53, 0xD4, 0x08, 0x08, 0x7A, 0x4A])
APP = bytearray([0x54, 0xBE, 0x2D, 0xE6, 0xB6, 0xB3, 0xF7, 0xC2,
                 0xD0, 0x33, 0x72, 0xB5, 0x27, 0x20, 0xD6, 0x2A ])
TTN_CONFIG = TTN(DEVADDR, NWKEY, APP, country="AS")
FPORT = 1
lora = uLoRa(
    cs=LORA_CS,
    sck=LORA_SCK,
    mosi=LORA_MOSI,
    miso=LORA_MISO,
    irq=LORA_IRQ,
    rst=LORA_RST,
    ttn_config=TTN_CONFIG,
    datarate=LORA_DATARATE,
    fport=FPORT
)
temp = 30
pa = 1000.1
hum = 50
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21)) #ESP32 Dev Board /myown
com = machine.UART(2,baudrate=9600,rx=34,tx=12,timeout=10) 
my_gps = MicropyGPS(7)
my_gps.local_offset
def get_GPS_values():    
    global gps_values,rtc 
    time.sleep(2)
    cc = com.readline()
    print (cc)
    for x in cc:
        my_gps.update(chr(x))
    gps_values = str(my_gps.latitude[0] + (my_gps.latitude[1] / 60)) + ',' + str(my_gps.longitude[0] + (my_gps.longitude[1] / 60))
    date = my_gps.date
    timestamp = my_gps.timestamp
    hour = timestamp[0]
    rtc = str(int(timestamp[0]))+":"+str(int(timestamp[1]))+":"+str(int(timestamp[2])) 
    return gps_values,rtc
counter = 0
while True:
  get_GPS_values()
  print("LAT,LONG",gps_values)
  lat,long=gps_values.split(",")
  print (float(lat))
  print (float(long))
  c = CayenneLPP()
  c.addTemperature(1, float(temp))
  c.addRelativeHumidity(2, float(hum)) 
  c.addBarometricPressure(3, float(pa))
  c.addGPS(7, float(lat), float(long),2.0 )
  data = c.getBuffer() # Get bytes
  lora.frame_counter=counter
  lora.send_data(data, len(data), lora.frame_counter)
  time.sleep(2)
  counter += 1