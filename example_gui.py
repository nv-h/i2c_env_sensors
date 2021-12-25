#!/usr/bin/env python3

from bme280 import BME280
from ccs811 import CCS811

import tkinter
import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.animation as animation


X_LIMIT = 100
RESOLUSION = 0.2


class GUI():
    def __init__(self):
        self.ccs811 = CCS811()
        self.bme280 = BME280()
        p, t, h = self.bme280.get()
        self.ccs811.compensate(h, t)

        self.data_co2 = np.zeros(int(X_LIMIT/RESOLUSION), dtype=int)
        self.data_t = np.zeros(int(X_LIMIT/RESOLUSION), dtype=int)
        self.data_h = np.zeros(int(X_LIMIT/RESOLUSION), dtype=int)
        self.data_p = np.zeros(int(X_LIMIT/RESOLUSION), dtype=int)

        self.root = tkinter.Tk()
        self.root.wm_title("Embedding in Tk anim")

        self.fig = Figure()
        # FuncAnimationより前に呼ぶ必要がある
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.

        x = np.arange(0, X_LIMIT, RESOLUSION)  # x軸(固定の値)
        self.l = np.arange(0, X_LIMIT, RESOLUSION)  # 表示期間(FuncAnimationで指定する関数の引数になる)
        plt_co2 = self.fig.add_subplot(211)
        plt_co2.set_ylim([0, 4000])
        self.line_co2, = plt_co2.plot(x, self.data_co2, 'C3', label="CO2 ppm")

        h0, l0 = plt_co2.get_legend_handles_labels()
        plt_co2.legend(h0, l0, loc='upper left')

        plt_t = self.fig.add_subplot(212)
        plt_t.set_ylim([-10, 50])
        self.line_t, = plt_t.plot(x, self.data_t, 'C1', label="Celsius")

        plt_h = plt_t.twinx()
        plt_h.set_ylim([0, 100])
        self.line_h, = plt_h.plot(x, self.data_h, 'C0', label="humidity %")

        plt_p = plt_t.twinx()
        plt_p.set_ylim([900, 1200])
        self.line_p, = plt_p.plot(x, self.data_p, 'C2', label="pressure hPa")

        h1, l1 = plt_t.get_legend_handles_labels()
        h2, l2 = plt_h.get_legend_handles_labels()
        h3, l3 = plt_p.get_legend_handles_labels()
        plt_t.legend(h1+h2+h3, l1+l2+l3, loc='upper left')

        self.ani = animation.FuncAnimation(self.fig, self.animate, self.l,
            init_func=self.init, interval=int(1000*RESOLUSION), blit=False,
            )

        toolbar = NavigationToolbar2Tk(canvas, self.root)
        canvas.get_tk_widget().pack(fill='both')

        button = tkinter.Button(master=self.root, text="Quit", command=self.quit)
        button.pack()


    def quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def init(self):  # only required for blitting to give a clean slate.
        self.line_co2.set_ydata(self.data_co2)
        return self.line_co2,


    def animate(self, i):
        try:
            p, t, h = self.bme280.get()
            voc, co2 = self.ccs811.get()
        except OSError:
            return

        print(f"{p:7.2f} hPa, {t:6.2f} C, {h:5.2f} %, TVOC:{voc:4d} ppb, eCO2:{co2:4d} ppm")
        self.data_co2 = np.append(self.data_co2[1:], co2)
        self.line_co2.set_ydata(self.data_co2)  # update the data_co2.

        self.data_t = np.append(self.data_t[1:], t)
        self.line_t.set_ydata(self.data_t)  # update the data_t.
        self.data_h = np.append(self.data_h[1:], h)
        self.line_h.set_ydata(self.data_h)  # update the data_h.
        self.data_p = np.append(self.data_p[1:], p)
        self.line_p.set_ydata(self.data_p)  # update the data_p.


    def run(self):
        tkinter.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.run()