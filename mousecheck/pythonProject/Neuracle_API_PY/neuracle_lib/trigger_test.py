import time

from triggerBox import TriggerIn

port_addr = "COM3"

port = TriggerIn(port_addr)
port.validate_device()


for i in range(10):
    port.output_event_data(i)
    time.sleep(10)