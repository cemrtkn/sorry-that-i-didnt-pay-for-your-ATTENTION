from gpiozero import MCP3008
from gpiozero.pins.rpigpio import RPiGPIOFactory  # Import RPi.GPIO pin factory
import time

# Set the pin factory to RPi.GPIO
factory = RPiGPIOFactory()

# Initialize the MCP3008 ADC with the specified pin factory
ldr1 = MCP3008(channel=0, pin_factory=factory)
ldr2 = MCP3008(channel=1, pin_factory=factory)
ldr3 = MCP3008(channel=2, pin_factory=factory)
ldr4 = MCP3008(channel=3, pin_factory=factory)

baseline1 = ldr1.value
baseline2 = ldr2.value
baseline3 = ldr3.value
baseline4 = ldr4.value
while True:
    x1 = (ldr1.value/baseline1)
    y1 = (ldr2.value/baseline2)
    y2 = (ldr3.value/baseline3)
    x2 = (ldr4.value/baseline4)
    print("X Value:", x1,x2)  # Read the LDR value (0.0 to 1.0)
    print("Y Value:", y1,y2)  # Read the LDR value (0.0 to 1.0)
    time.sleep(0.5)