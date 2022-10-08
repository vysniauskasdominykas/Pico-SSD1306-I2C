import time
import machine
import framebuf

# Reference:
# https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf
# pages 26-32.

# Fundamental commands
SSD1306_SET_CONTRAST = 0x81
SSD1306_SET_ENTIRE_DISPLAY_RESUME_CONTENT = 0xA4
SSD1306_SET_ENTIRE_DISPLAY_IGNORE_CONTENT = 0xA5
SSD1306_SET_INVERSE_DISPLAY_OFF = 0xA6
SSD1306_SET_INVERSE_DISPLAY_ON = 0xA7
SSD1306_SET_DISPLAY_OFF = 0xAE
SSD1306_SET_DISPLAY_ON = 0xAF

# Scrolling commands
SSD1306_SET_HORIZONTAL_SCROLL_RIGHT = 0x26
SSD1306_SET_HORIZONTAL_SCROLL_LEFT = 0x27
SSD1306_SET_VERTICAL_AND_HORIZONTAL_SCROLL_RIGHT = 0x29
SSD1306_SET_VERTICAL_AND_HORIZONTAL_SCROLL_LEFT = 0x2A
SSD1306_SET_SCROLL_DEACTIVATE = 0x2E
SSD1306_SET_SCROLL_ACTIVATE = 0x2F
SSD1306_SET_VERTICAL_SCROLL_AREA = 0xA3

# Addressing commands
SSD1306_SET_LOWER_COLUMN_START_ADDRESS_FOR_PAGE_ADDRESSING_MODE = 0x00
SSD1306_SET_HIGHER_COLUMN_START_ADDRESS_FOR_PAGE_ADDRESSING_MODE = 0x10
SSD1306_SET_MEMORY_ADDRESSING_MODE = 0x20
SSD1306_SET_COLUMN_ADDRESS = 0x21
SSD1306_SET_PAGE_ADDRESS = 0x22
SSD1306_SET_PAGE_START_ADDRESS_FOR_PAGE_ADDRESSING_MODE = 0xB0

# Hardware configuration commands
SSD1306_SET_DISPLAY_START_LINE = 0x40
SSD1306_SET_SEGMENT_REMAP_INVERSE = 0xA0
SSD1306_SET_SEGMENT_REMAP_NORMAL = 0xA1
SSD1306_SET_MULTIPLEX_RATIO = 0xA8
SSD1306_SET_COM_OUTPUT_SCAN_DIRECTION_INVERSE = 0xC0
SSD1306_SET_COM_OUTPUT_SCAN_DIRECTION_NORMAL = 0xC8
SSD1306_SET_DISPLAY_OFFSET = 0xD3
SSD1306_SET_COM_PINS_HARDWARE_CONFIGURATION = 0xDA

# Timing & driving commands
SSD1306_SET_DISPLAY_CLOCK_DIVIDE_RATIO = 0xD5
SSD1306_SET_PRE_CHARGE_PERIOD = 0xD9
SSD1306_SET_VCOMH_DESELECT_LEVEL = 0xDB
SSD1306_SET_NO_OPERATION = 0xE3

class SSD1306I2C(framebuf.FrameBuffer):
    def __init__(self, display_width=128, display_height=32, gpio_serial_data=16, gpio_serial_clock=17):
        self.DISPLAY_WIDTH = display_width
        self.DISPLAY_HEIGHT = display_height

        self.serial_interface = machine.I2C(0, sda=machine.Pin(gpio_serial_data), scl=machine.Pin(gpio_serial_clock))
        
        self.frame_data = bytearray(self.DISPLAY_WIDTH * self.DISPLAY_HEIGHT // 8)
        super().__init__(self.frame_data, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, framebuf.MONO_VLSB)
        
        self.write_initialization_sequence()
        self.render()
        
    def write_initialization_sequence(self):
        self.write_command(SSD1306_SET_DISPLAY_OFF)
        
        self.write_command(SSD1306_SET_CONTRAST, value=0xFF)
        self.write_command(SSD1306_SET_PRE_CHARGE_PERIOD, value=0xF1)
        self.write_command(SSD1306_SET_VCOMH_DESELECT_LEVEL, value=0x40)
        
        self.write_command(SSD1306_SET_DISPLAY_START_LINE)
        self.write_command(SSD1306_SET_DISPLAY_OFFSET, value=0x00)
        self.write_command(SSD1306_SET_DISPLAY_CLOCK_DIVIDE_RATIO, value=0x80)
        
        if (self.DISPLAY_WIDTH != 64) and (self.DISPLAY_HEIGHT == 16 or self.DISPLAY_HEIGHT == 32):
            self.write_command(SSD1306_SET_COM_PINS_HARDWARE_CONFIGURATION, value=0x02)
        else:
            self.write_command(SSD1306_SET_COM_PINS_HARDWARE_CONFIGURATION, value=0x12)
            
        self.write_command(SSD1306_SET_SEGMENT_REMAP_NORMAL)
        self.write_command(SSD1306_SET_COM_OUTPUT_SCAN_DIRECTION_NORMAL)
        self.write_command(SSD1306_SET_MULTIPLEX_RATIO, value=self.DISPLAY_HEIGHT-1)
        self.write_command(SSD1306_SET_MEMORY_ADDRESSING_MODE, value=0x00)
        
        self.write_command(SSD1306_SET_ENTIRE_DISPLAY_RESUME_CONTENT);
        self.write_command(SSD1306_SET_INVERSE_DISPLAY_OFF);
        self.write_command(SSD1306_SET_DISPLAY_ON);
    
    def write_command(self, command, value=None):
        self.serial_interface.writeto(0x3C, bytearray([0x80, command]))
        
        if value != None:
            self.write_command(value)

    def write_buffer(self, buffer):
        self.serial_interface.writevto(0x3C, [bytearray([0x40]), buffer])
        
    def render(self):
        self.write_command(SSD1306_SET_COLUMN_ADDRESS)
        self.write_command(0)
        self.write_command(self.DISPLAY_WIDTH - 1)
        
        self.write_command(SSD1306_SET_PAGE_ADDRESS)
        self.write_command(0)
        self.write_command(self.DISPLAY_HEIGHT // 8 - 1)

        self.write_buffer(self.frame_data)

    def clear(self):
        self.fill(0x00)
        self.render()
