# HBARPi
HBARPi is a Python based tracking tool for Hedera Hashgraph, aimed to be run on a Raspberry Pi with GPIO displays. It connects to gate.io and pulls your HBAR balance from mainnet.

### Prerequisites:
This project was built using a Waveshare OLED Display which uses the SSD1306 drivers in Python. It is possible to run on other OLED displays (eg Adafruit), but you will need to locate and integrate the device specific drivers manually.

1. Almost any RaspberryPi (with GPIO support):
    - https://thepihut.com/collections/raspberry-pi/products/raspberry-pi-zero-wh-with-pre-soldered-header
2. A SPI/I2C GPIO display (Using the SSD1306 Device Driver):
    - https://thepihut.com/collections/raspberry-pi-screens/products/128x32-2-23inch-oled-display-hat-for-raspberry-pi
3. SD Card 8GB or higher -- image it with Raspberry Pi OS Lite
4. Power Cable & Charger/Battery Bank

### Build the Device:
1. Burn the OS in SD Card with Raspberry Pi Imager
    - https://www.raspberrypi.org/software/
2. Connect the display to Pi GPIO Pins
3. Plug in Power
4. Install OS
5. Enable SPI in Raspi Config
    - sudo raspi-config
    - select Interface Options > SPI > Yes
6. Reboot the Pi
    - sudo reboot now

### Software & Install:
1. Get your HBAR Wallet Address
2. Install Python3, Git, and SPI
    - sudo apt-get update
    - sudo apt-get install python3-pip
    - sudo apt-get install python3-pil
    - sudo apt-get install python3-numpy
    - sudo pip3 install RPi.GPIO
    - sudo pip3 install spidev
    - sudo pip3 install ccxt
    - sudo pip3 install schedule
    - sudo apt-get install git
3. clone this project to RaspberryPi
    - git clone https://github.com/D-Pyro/HBARPi
4. Edit config.py in nano or other text editor and add your wallet
    - nano HBARPi/config.py
    - or open with text editor
    - Then fill in the HBAR Wallet Address

### Run
1. Change to project folder
    - cd HBARPi
2. Run it with Python3 
    - sudo python3 main.py