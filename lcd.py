import machine # type: ignore
import time

class LCD:
    def __init__(self, addr=None, blen=1):
        sda = machine.Pin(6)
        scl = machine.Pin(7)
        self.bus = machine.I2C(1, sda=sda, scl=scl, freq=400000)
        self.addr = self.scan_address(addr)
        self.blen = blen
        self.initialize_display()

    def scan_address(self, addr):
        devices = self.bus.scan()
        if not devices:
            raise Exception("No LCD found")
        if addr is not None:
            if addr in devices:
                return addr
            else:
                raise Exception(f"LCD at 0x{addr:02X} not found")
        elif 0x27 in devices:
            return 0x27
        elif 0x3F in devices:
            return 0x3F
        else:
            raise Exception("No LCD found")

    def initialize_display(self):
        self.send_command(0x33)  # Initialize to 8-bit mode
        time.sleep(0.005)
        self.send_command(0x32)  # Switch to 4-bit mode
        time.sleep(0.005)
        self.send_command(0x28)  # Set 2 lines and 5x7 matrix
        time.sleep(0.005)
        self.send_command(0x0C)  # Display ON, cursor OFF
        time.sleep(0.005)
        self.clear()
        self.enable_backlight()

    def write_word(self, data):
        if self.blen == 1:
            data |= 0x08  # Turn on backlight
        else:
            data &= 0xF7  # Turn off backlight
        self.bus.writeto(self.addr, bytearray([data]))

    def send_command(self, cmd):
        self.write_word(cmd & 0xF0 | 0x04)  # Send higher nibble
        time.sleep(0.002)
        self.write_word(cmd & 0xF0)  # EN=0

        self.write_word((cmd << 4) & 0xF0 | 0x04)  # Send lower nibble
        time.sleep(0.002)
        self.write_word((cmd << 4) & 0xF0)  # EN=0

    def send_data(self, data):
        self.write_word(data & 0xF0 | 0x05)  # Send higher nibble with RS=1
        time.sleep(0.002)
        self.write_word(data & 0xF0)  # EN=0

        self.write_word((data << 4) & 0xF0 | 0x05)  # Send lower nibble with RS=1
        time.sleep(0.002)
        self.write_word((data << 4) & 0xF0)  # EN=0

    def clear(self):
        self.send_command(0x01)  # Clear display

    def enable_backlight(self):
        self.blen = 1
        self.write_word(0x08)  # Turn on backlight

    def disable_backlight(self):
        self.blen = 0
        self.write_word(0x00)  # Turn off backlight

    def write(self, x, y, text):
        if not (0 <= x <= 15) or not (0 <= y <= 1):
            raise ValueError("x or y out of bounds")
        addr = 0x80 + 0x40 * y + x
        self.send_command(addr)

        for char in text:
            self.send_data(ord(char))

    def message(self, text):
        for char in text:
            if char == '\n':
                self.send_command(0xC0)  # Move to the second line
            else:
                self.send_data(ord(char))

"""
LCDで、文字列を表示
"""
lcd = LCD()
lcd.message("Hello World!")
time.sleep(2)
lcd.clear()


lcd.message("Micro Python")
time.sleep(2)
lcd.clear()

# LCD1602は、日本語フォントに対応していないので、文字化けをする
lcd.write(0, 0, "電子工作の世界へようこそ!")
time.sleep(2)
lcd.clear()
