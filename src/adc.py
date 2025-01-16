from gpiozero import MCP3008
from gpiozero.pins.rpigpio import RPiGPIOFactory  # Import RPi.GPIO pin factory
import time

# Set the pin factory to RPi.GPIO
factory = RPiGPIOFactory()

# Initialize the MCP3008 ADC with the specified pin factory
ldr1 = MCP3008(channel=0, pin_factory=factory)
ldr2 = MCP3008(channel=1, pin_factory=factory)
baseline = ldr1.value
while True:
    x = 1 - (ldr1.value/baseline)
    y = 1 - (ldr2.value/baseline)
    print("LDR1 Value:", x)  # Read the LDR value (0.0 to 1.0)
    print("LDR2 Value:", y)  # Read the LDR value (0.0 to 1.0)
    time.sleep(0.5)