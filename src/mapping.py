from gpiozero import MCP3008
from gpiozero.pins.rpigpio import RPiGPIOFactory  # Import RPi.GPIO pin factory
import time

def calculate_position(up_down, right_left):
    # normalize the ratios
    ldr1_norm, ldr2_norm = up_down
    ldr3_norm, ldr4_norm = right_left
    
    # comoute contributions to x and y
    y = ldr1_norm - ldr2_norm
    x = ldr4_norm - ldr3_norm
    
    # normalize the coordinates
    magnitude = max(abs(x), abs(y),1)
    x /= magnitude
    y /= magnitude
    
    return x,y
    
    
    
# Set the pin factory to RPi.GPIO
factory = RPiGPIOFactory()
ldr1 = MCP3008(channel=0, pin_factory=factory)
ldr2 = MCP3008(channel=1, pin_factory=factory)
ldr3 = MCP3008(channel=2, pin_factory=factory)
ldr4 = MCP3008(channel=3, pin_factory=factory)

baseline1 = ldr1.value
baseline2 = ldr2.value
baseline3 = ldr3.value
baseline4 = ldr4.value

while True:
    
    up_down = [(ldr1.value/baseline1),(ldr2.value/baseline2)]
    right_left = [(ldr3.value/baseline3),(ldr4.value/baseline4)]
    
    x,y = calculate_position(up_down, right_left)
    
    
    print("Up-down")
    print(y)
    print("-"*40)
    print("Right-left")
    print(x)
    print("-"*40)
    
    time.sleep(0.5)