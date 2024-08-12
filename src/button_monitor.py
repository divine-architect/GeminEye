import lgpio
import subprocess
import time
import os

BUTTON_PIN_1 = 17
BUTTON_PIN_2 = 26
BUTTON_PIN_3 = 22

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, BUTTON_PIN_1, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(h, BUTTON_PIN_2, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(h, BUTTON_PIN_3, lgpio.SET_PULL_UP)

print("Waiting for button presses...")

def execute_script(script_name):
    full_path = os.path.join(script_dir, script_name)
    print(f"Executing {full_path}")
    subprocess.run(["python3", full_path])
    print("Script execution completed")

def wait_for_button_release(pin):
    while lgpio.gpio_read(h, pin) == 0:
        time.sleep(0.1)
    time.sleep(0.1)  # Debounce delay

try:
    while True:
        if lgpio.gpio_read(h, BUTTON_PIN_1) == 0:
            wait_for_button_release(BUTTON_PIN_1)
            execute_script("justgemini.py")
        
        elif lgpio.gpio_read(h, BUTTON_PIN_2) == 0:
            wait_for_button_release(BUTTON_PIN_2)
            execute_script("gemini_with_cam.py")
        
        elif lgpio.gpio_read(h, BUTTON_PIN_3) == 0:
            wait_for_button_release(BUTTON_PIN_3)
            execute_script("date_time.py")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    lgpio.gpiochip_close(h)
