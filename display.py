import threading
import time
from datetime import datetime, timedelta
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix

class Display(threading.Thread):
    def __init__(self, weather, dimmer):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        if weather is not None: 
            self._weather = weather
        self._dimmer = dimmer

        # Configure LED matrix driver
        self._matrix = RGBMatrix(32, 2, 1)
        self._matrix.pwmBits = 11
        self._matrix.brightness = 25

        # Load fonts
        self._font_large = graphics.Font()
        self._font_large.LoadFont("rpi-rgb-led-matrix/fonts/9x18B.bdf")
        self._font_medium = graphics.Font()
        self._font_medium.LoadFont("rpi-rgb-led-matrix/fonts/6x10.bdf")
        self._font_small = graphics.Font()
        self._font_small.LoadFont("rpi-rgb-led-matrix/fonts/5x7.bdf")

        # Define colors
        self._white = graphics.Color(255, 255, 255)
        self._green = graphics.Color(50, 255, 50)
        self._red = graphics.Color(255, 0, 0)

        self._future = datetime.now() + timedelta(seconds=20)


    def _countdown(self, canvas):
        time_now = datetime.now()

        if time_now < self._future:
            remainder = str(self._future - time_now)[2:7]
            graphics.DrawText(canvas, self._font_large, 10, 21, self._red, remainder)
        else:
            graphics.DrawText(canvas, self._font_large, 10, 21, self._red, "00:00")

    def _clock(self, canvas):
        time_now = datetime.now()
        is_420 = time_now.hour == 4 and time_now.minute == 20

        if is_420:
            color = self._green  
        else:
            color = self._white

        # Current time
        graphics.DrawText(canvas, self._font_medium, 9, 13, color, time_now.strftime("%H:%M:%S"))

        if is_420:
            graphics.DrawText(canvas, self._font_small, 12, 25, color, 'blaze it')
        else:
            # Alternating date & weather
            if (int(time.time()) % 10) > 4 and self._weather.temp_now is not None: 
                temp_str_now = "%3.0f" % self._weather.temp_now
                temp_str_now = temp_str_now + 'c'
                center = (64 - (len(temp_str_now) * 6) - 2) / 2 - 1  # 6 = 5 char pixels + 2 space pixels - 2 for end
                graphics.DrawText(canvas, self._font_small, center, 25, color, temp_str_now)
            else:
                graphics.DrawText(canvas, self._font_small, 8, 25, color, time_now.strftime("%a %b %-d"))


    def _draw(self, canvas):
        canvas.Clear()
        # self._countdown(canvas)
        self._clock(canvas)

    def run(self):
        canvas = self._matrix.CreateFrameCanvas()

        while True:
            self._draw(canvas)
            time.sleep(0.05)
            canvas = self._matrix.SwapOnVSync(canvas)
            self._matrix.brightness = self._dimmer.brightness
