import board
import asyncio
import busio
import rotaryio
import digitalio
import displayio
import terminalio
import adafruit_displayio_ssd1306
import i2cdisplaybus
from tm1637_display import TM1637Display
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label

#7 Segment display setup
SEG_CLK = board.GP5
SEG_DIO = board.GP4
segment_display = TM1637Display(SEG_CLK, SEG_DIO, length=4, 
                        auto_write=True, brightness=1)

#Encoder setup
ENC_A = board.GP14
ENC_B = board.GP15
ENC_SW = board.GP13
enc = rotaryio.IncrementalEncoder(ENC_A, ENC_B)
enc_btn = digitalio.DigitalInOut(ENC_SW)

#OLED setup
displayio.release_displays()
OLED_SDA = board.GP8
OLED_SCL = board.GP9
i2c = busio.I2C(OLED_SCL, OLED_SDA)
oled_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3c)
oled = adafruit_displayio_ssd1306.SSD1306(oled_bus, width=128, height=64)

#bitmap label test
splash = displayio.Group()
text = "Hello world"
text_area = bitmap_label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=10, y=10)
splash.append(text_area)
oled.root_group = splash


async def segment():
    counter = 5
    blink = True
    
    while True:
        if counter >= 0:
            mins = counter // 60
            secs = counter % 60
            time_str = f"{mins:02d}.{secs:02d}"
            segment_display.print(time_str)
            counter -= 1
            await asyncio.sleep(1)

        elif blink:
            segment_display.clear()
            blink = False
            await asyncio.sleep(.5)
        else:
            segment_display.print("00.00")
            blink = True
            await asyncio.sleep(.5)

async def encoder():
    enc_last = None
    btn_last = None

    while True:
        if enc.position != enc_last:
            enc_last = enc.position
            print(f"encoder position = {enc.position}")
        
        if enc_btn.value != btn_last:
            btn_last = enc_btn.value
            print(f"button: {enc_btn.value}")

        await asyncio.sleep(0)

        

async def main():
    segment_task = asyncio.create_task(segment())
    encoder_task = asyncio.create_task(encoder())

    await asyncio.gather(segment_task)
    await asyncio.gather(encoder_task)

asyncio.run(main())