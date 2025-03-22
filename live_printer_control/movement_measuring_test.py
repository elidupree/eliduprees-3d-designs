import time
import matplotlib.pyplot as plt

from connection import PrinterConnection

positions = []

def on_position_report(position):
    positions.append((position, time.time()))

def derivatives(xs):
    return [((x1-x0)/(t1-t0), (t0+t1)/2) for (x0,t0),(x1,t1) in zip(xs[:-1],xs[1:])]

def plot_xs(xs):
    plt.plot([t for x,t in xs], [x for x,t in xs])

# plt.plot([1,2,3,4])
# plt.show()
with PrinterConnection(on_position_report = on_position_report) as connection:
    connection.send("G91")
    connection.send("M201 X2")
    connection.send("G0 X10 F180")
    time.sleep(0.1)
    connection.send("G0 X10 F9999")
    connection.send("G0 X-20")
    while connection.planning_buffer_count() + connection.unprocessed_buffer_count() > 0:
        connection.send("M114 R")
        time.sleep(0.1)

xs = [(p.x,t) for p,t in positions]
velocities = derivatives(xs)
accelerations = derivatives(velocities)

plot_xs(xs)
plot_xs(velocities)
# plot_xs(accelerations)
plt.show()