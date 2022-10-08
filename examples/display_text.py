import ssd1306

display = ssd1306.SSD1306I2C()
display.text("123", 0, 0)
display.render()