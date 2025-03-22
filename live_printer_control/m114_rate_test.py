import time

from connection import PrinterConnection

count = 0

def on_position_report(position):
    connection.send("M114 R")
    global count
    count += 1

with PrinterConnection(on_position_report = on_position_report) as connection:
    connection.send("M114 R")
    print(count)
    time.sleep(1)
    print(count)

print(count)