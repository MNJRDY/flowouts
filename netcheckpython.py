import ctypes
import time
import psutil
import speedtest
from plyer import notification
import logging
import threading
import signal
import sys

# Configure logging
logging.basicConfig(filename='netcheck.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Define the threshold speed in Mbps
threshold_speed = 5000
stop_event = threading.Event()

# Function to check internet speed
def test_internet_speed():
    logging.info("Testing internet speed.")
    st = speedtest.Speedtest()
    st.download()
    download_speed = st.results.download / (1024 * 1024)  # Convert to Mbps
    logging.info(f"Download speed: {download_speed} Mbps")
    print("internet speed ------>",download_speed)
    return download_speed

# Function to show notification
def show_notification(message):
    notification.notify(
        title='Internet Speed Checker',
        message=message,
        app_icon=None,
        timeout=10,
    )
    logging.info(f"Notification shown: {message}")

# Function to check internet speed and notify if below threshold
def check_internet_speed():
    current_speed = test_internet_speed()
    if current_speed < threshold_speed:
        show_notification("Check your internet connection for better connectivity.")

# Function to monitor network changes
def monitor_network_change():
    last_status = None
    while not stop_event.is_set():
        current_status = psutil.net_if_stats()
        if current_status != last_status:
            last_status = current_status
            logging.info("Network status changed.")
            check_internet_speed()
        time.sleep(10)

# Function to monitor screen lock/unlock events
def monitor_screen_lock_unlock():
    user32 = ctypes.windll.User32
    kernel32 = ctypes.windll.Kernel32
    h_wnd = kernel32.GetConsoleWindow()
    
    while not stop_event.is_set():
        if user32.GetForegroundWindow() != h_wnd:
            logging.info("Screen unlocked.")
            check_internet_speed()
            while user32.GetForegroundWindow() != h_wnd and not stop_event.is_set():
                time.sleep(1)
        time.sleep(1)

# Signal handler to stop the script
def signal_handler(sig, frame):
    logging.info("Stopping the script.")
    stop_event.set()
    sys.exit(0)

# Run the monitors
if __name__ == "__main__":
    logging.info("Starting the script.")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    network_thread = threading.Thread(target=monitor_network_change)
    screen_thread = threading.Thread(target=monitor_screen_lock_unlock)

    network_thread.start()
    screen_thread.start()

    network_thread.join()
    screen_thread.join()
