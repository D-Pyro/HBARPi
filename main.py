import config
import time
import numpy as np
import ccxt
import requests

if config.RUN_EMULATOR:
    import cv2
else:
    import sys
    sys.path.append('./drivers')
    import SPI
    import SSD1305

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def inverse_lerp(a, b, value):
    if a != b:
        return clamp((value - a) / (b - a), 0, 1)
    return 0

def lerp(a, b, t):
    return a + (b-a) * clamp(t, 0, 1)

def get_balance():
    url = "https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{0}".format(config.WALLET_ADDRESS)
    return ((requests.get(url).json()["balance"]["balance"]) * (0.00000001))

def get_exchange_rate():
   url = "https://open.er-api.com/v6/latest/USD"
   return (float)(requests.get(url).json()["rates"]["{0}".format(config.LOCAL_CURRENCY_SYMBOL)])

if config.RUN_EMULATOR:
    imageEncoding = 'RGB'
else:
    imageEncoding = '1'
    # Raspberry Pi pin configuration:
    RST = None     # on the PiOLED this pin isnt used
    # Note the following are only used with SPI:
    DC = 24
    SPI_PORT = 0
    SPI_DEVICE = 0

    # 128x32 display with hardware SPI:
    disp = SSD1305.SSD1305_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
    # Initialize library.
    disp.begin()
    # Clear display.
    disp.clear()
    disp.display()    

frameSize = (128, 32)

titleFont = ImageFont.truetype("fonts/04B_03__.TTF", 8)
splashFont = ImageFont.truetype("fonts/OpenSans-Regular.ttf", 9)
balanceFont = ImageFont.truetype("fonts/OpenSans-Regular.ttf", 14)
hbarFont_large = ImageFont.truetype("fonts/aAtmospheric.ttf", 14)
currencyFont = ImageFont.truetype("fonts/lilliput steps.ttf", 8)
logoFont = ImageFont.truetype("fonts/OpenSans-Regular.ttf", 12)

arrow = Image.open('images/arrow.bmp').convert(imageEncoding)
arrow = arrow.resize((8, 8), Image.ANTIALIAS)

previousBalance = 0
currentBalance = 0

previousRate = 0
currentRate = 0

previousPerc = 0
currentPerc = 0

startTime = time.time()
timeDelta = 0

displayTime = 60/3
screenToShow = 0

exchange = ccxt.gateio()

def update_data():
    global previousBalance
    global currentBalance

    global previousRate
    global currentRate

    global previousPerc
    global currentPerc

    previousBalance = currentBalance
    try:
        currentBalance = get_balance()
    except:
        currentBalance = previousBalance
        pass

    try:
        ticker = exchange.fetch_ticker("HBAR/USDT")
    except:
        pass

    previousRate = currentRate        
    currentRate = (float)(ticker['info']['last'])
    
    previousPerc = currentPerc
    currentPerc = (float)(ticker['info']['percentChange'])

update_data()

try:
    localExchange = get_exchange_rate()
except:
    localExchange = 1

while True:

    if (time.time() - startTime) > displayTime:
        startTime = time.time()

        update_data()

        screenToShow += 1
        if screenToShow > 2:
            screenToShow = 0

    if screenToShow == 0:

        flip = False
        time2 = np.arange(0, 1, 0.1)
        screen_x_offset = np.sin((time.time() * 3.5))

        if screen_x_offset < 0:
            flip = True
        else:
            flip = False

        pix = (int)(lerp(5, 29, abs(screen_x_offset)))
        canvas = Image.new(imageEncoding, (frameSize))
        image = Image.open('images/hbar_logo.bmp').convert(imageEncoding)
        if flip:
            image = ImageOps.mirror(image)
        image = image.resize((pix, 28), Image.ANTIALIAS)
        canvas.paste(image, (28 - (int)(pix * 0.5) - 12, 2))

        draw = ImageDraw.Draw(canvas)
        draw.text((32, 11), "Hedera Hashgraph", fill='white', font=splashFont)
        draw.text((70, 32-9), "Tracker (v0.2)", fill='white', font=titleFont)

        if (time.time() - startTime) > 8:
            startTime = time.time()
            screenToShow += 1

    if screenToShow == 1:
        
        canvas = Image.new(imageEncoding, (frameSize))
        draw = ImageDraw.Draw(canvas)
        draw.text((0, -1), "HBAR Balance (" + config.LOCAL_CURRENCY_SYMBOL + ")", fill='white', font=titleFont)
        draw.text((1, 9), u'\u0126', fill='white', font=logoFont)
        draw.text((15, 7), "{:,.2f}".format(lerp(previousBalance, currentBalance, timeDelta)), fill="white", font=balanceFont)

        draw.text((0, 32-8), "=" + config.LOCAL_CURRENCY_CHAR, fill='white', font=currencyFont)
        draw.text((12, 32-6), "{:,.2f} @ S{:,.9f}".format((lerp(previousBalance, currentBalance, timeDelta) * lerp(previousRate, currentRate, timeDelta)) * localExchange, lerp(previousRate, currentRate, timeDelta) * localExchange), fill='white', font=titleFont)   

    if screenToShow == 2:

        canvas = Image.new(imageEncoding, (frameSize))
        draw = ImageDraw.Draw(canvas)
        draw.text((0, -1), "HBAR Price (USDT)", fill='white', font=titleFont)
        draw.text((1, 10), "$", fill='white', font=hbarFont_large)
        draw.text((17, 7), "{:,.9f}".format(lerp(previousRate, currentRate, timeDelta)), fill="white", font=balanceFont)
        
        sign = currentRate - previousRate

        if sign > 0:
            arrow2 = ImageOps.flip(arrow)
            canvas.paste(arrow2, (105, 12))
        if sign < 0:
            canvas.paste(arrow, (105, 12))

        perc24 = lerp(previousPerc, currentPerc, timeDelta)
        includeSign = ""
        if perc24 > 0:
            includeSign = "+"
        
        draw.text((2, 32-6), "24h {}{:,.2f}%".format(includeSign, perc24), fill='white', font=titleFont)    


    timeDelta = inverse_lerp(0, displayTime, time.time() - startTime)

    if config.RUN_EMULATOR:
        # Virtual display
        npImage = np.asarray(canvas)
        frameBGR = cv2.cvtColor(npImage, cv2.COLOR_RGB2BGR)
        cv2.imshow('HashAPI', frameBGR)
        k = cv2.waitKey(16) & 0xFF
        if k == 27:
            break
    else:
        # Hardware display
        disp.image(canvas)
        disp.display()
        time.sleep(1./60)

if config.RUN_EMULATOR:
    # Virtual display
    cv2.destroyAllWindows()
else:
    # Hardware display
    pass
