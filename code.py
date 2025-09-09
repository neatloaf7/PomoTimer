import board
import asyncio
import busio
import rotaryio
import digitalio
import displayio
import terminalio
import adafruit_displayio_ssd1306
import time
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
enc = rotaryio.IncrementalEncoder(ENC_B, ENC_A)
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

#class for encoder state
class EncoderMsg:
    TURN = 0
    CLICK = 1
    def __init__(self, kind, delta=0):
        self.kind = kind
        self.delta = delta

#method for updating 7 segment display
def show(self, segments):
    segment_display.print(segments)

#Create queue to watch encodermsg updates
enc_q = asyncio.Queue(8)

#Encoder task that updates EncoderMsg
async def encoder():
    last_pos = enc.position
    last_btn = enc_btn.value
    
    while True:
        pos = enc.position
        if pos != last_pos:
            await enc_q.put(EncoderMsg(EncoderMsg.TURN, pos-last_pos))
            last_pos = pos

        if not enc_btn.value and last_btn:
            await enc_q.put(EncoderMsg(EncoderMsg.CLICK))
        
        last_btn = enc_btn.value
        await asyncio.sleep(0.02)

#state machine for holding global variables and display state
class App:
    #initialize state and queue
    def __init__(self):
        self.q = enc_q
        self.state = "MAIN_MENU"
        self.oled_on = True
        self.last_enc_time = time.monotonic() #used for oled or full sleep
        self.IDLE_LIMIT = 10
        self.timer_mode = "NONE" #POM or MAN
        self.pomophase = 0
        self.minutes = 0
        self.seconds = 0
        self.editing = True
        self.working = True

    async def run(self):
        while True:
            if self.state == "MAIN_MENU":
                await self.main_menu()
            elif self.state == "POMODORO":
                await self.pomodoro()
            elif self.state == "MANUAL":
                await self.manual()
            elif self.state == "COUNTING":
                await self.counting()
            elif self.state == "FINISHED":
                await self.finished()
            elif self.state == "SLEEP":
                await self.sleep()

app = App()

#main menu
async def main_menu(self):
    opts = ["Pomodoro", "Manual", "Sleep"]
    idx = 0
    
    #put opts on oled
    #initialize triangle object on first opt
    while True:
        #wait for update from encoder for 10s, otherwise go sleep
        try:
            msg = await asyncio.wait_for(self.q.get(), timeout=10)
        except asyncio.TimeoutError:
            self.state = "SLEEP"
            return

        if msg.kind == EncoderMsg.TURN:
            idx = (idx + msg.delta) % len(opts)
            #update triangle position
        elif msg.kind == EncoderMsg.CLICK: #on click update state then pass back to app loop
            if idx == 0:
                self.state = "POMODORO"
                return
            elif idx == 1:
                self.state = "MANUAL"
                return
            else:
                self.state = "SLEEP"
                return

#pomodoro timer
async def pomodoro(self):
    pick_int = False
    opts = ["Start", "Intervals", "Back"]
    idx = 0

    while True:
        try:
            msg = await asyncio.wait_for(self.q.get(), timeout=10)
        except asyncio.TimeoutError:
            self.state = "SLEEP"
            return

        if pick_int:
            if msg.kind == EncoderMsg.TURN:
                do = "something"
                #scroll the interval number
            elif msg.kind == EncoderMsg.CLICK:
                pick_int = False
                #dehighlight interval option
        else:
            if msg.kind == EncoderMsg.TURN:
                idx = (idx + msg.delta) % len(opts)
                #update triangle
            elif msg.kind == EncoderMsg.CLICK:
                if idx == 0:
                    start = "timer"
                    self.working = True
                    self.state = "COUNTING"
                    return
                elif idx == 1:
                    pick_int = True
                    #higlight the interval option
                elif idx == 2:
                    self.state = "MAIN_MENU"
                    return

#manual timer
async def manual(self):
    edit_pos = 0 #0 minutes 1 seconds
    opts = ["Start", "Set Time" "Back"]
    idx = 1
    #highligh set time

    while True:
        try:
            msg = await asyncio.wait_for(self.q.get(), timeout=10)
        except asyncio.TimeoutError:
            self.state = "SLEEP"
            return
    
        if self.editing:
            if msg.kind == EncoderMsg.TURN:
                if edit_pos == 0:
                    edit = "Minutes"
                    #edit the minutes, blink the minutes digits
                    mins = mins + msg.delta
                else:
                    edit = "seconds"
                    secs = secs + msg.delta
                self.show(f"{mins}.{secs}")

            elif msg.kind == EncoderMsg.CLICK:
                if edit_pos == 0:
                    edit_pos = 1
                else:
                    edit_pos = 0
                    self.editing = False
                    #unhighlight set time
                    idx = 0
        
        else:
            if msg.kind == EncoderMsg.TURN:
                idx = (idx + msg.delta) % len(opts)
            elif msg.kind == EncoderMsg.CLICK:
                if idx == 0:
                    self.state = "COUNTING"
                    return
                elif idx == 1:
                    self.editing = True
                else:
                    self.state = "MAIN_MENU"
                    return
                
async def counting(self):
    await asyncio.gather(self.count(), self.count_menu())

async def count(self):
    

async def count_menu(self):
    opts =


    #old counting

    total = self.minutes*60 + self.seconds
    self.paused = False

    while total > 0:

        try:
            await asyncio.wait_for(self.q.get(), timeout=1) #wait for enc or 1 sec
            do = "something" #scroll menu
        except asyncio.TimeoutError:
            if not self.paused:
                self.show("stuff")
                total -= 1

    if self.timer_mode == "POMO":
        self.pomophase -= 1
    self.state = "FINISHED"
    return

async def finished(self):
    #play da finish animation, wait for encoder or 10 sec
    opts = ["Start", "Cancel"]
    idx = 0

    try:
        msg = await asyncio.wait_for(self.q.get(), timeout=10)
    except asyncio.TimeoutError:
        pass

    #cancel da animation
    #if manual timer, go back to manul
    if self.timer_mode == "MAN":
        self.state = "MANUAL"
        return

    #if pomo timer, go to pomo select
    while True:
        try:
            msg = await asyncio.wait_for(self.q.get(), timeout=10)
        except asyncio.TimeoutError:
            self.state = "SLEEP"
            return
        
        if msg.kind == EncoderMsg.TURN:
            idx = (idx + msg.delta) % len(opts)

    





async def segment():
    counter = 10
    shower = 21
    blink = True
    
    while True:
        if counter >= 0:
            mins = counter // 60
            secs = counter % 60
            time_str = f"{mins:02d}.{secs:02d}"
            segment_display.print(time_str)
            counter -= 1
        
        
        else:
            segment_display.print("11. 1")

        await(asyncio.sleep(0.02))
    

        # elif blink:
        #     segment_display.clear()
        #     blink = False
        #     await asyncio.sleep(.5)
        # else:
        #     segment_display.print("00.00")
        #     blink = True
        #     await asyncio.sleep(.5)

# async def encoder():
#     enc_last = enc.position
#     btn_last = enc_btn.value

#     while True:
#         if enc.position != enc_last:
#             enc_last = enc.position
#             print(f"encoder position = {enc.position}")
        
#         if enc_btn.value != btn_last:
#             btn_last = enc_btn.value
#             print(f"button: {enc_btn.value}")

#         await asyncio.sleep(0)

        

async def main():
    segment_task = asyncio.create_task(segment())
    encoder_task = asyncio.create_task(encoder())

    await asyncio.gather(segment_task)
    await asyncio.gather(encoder_task)

asyncio.run(main())

