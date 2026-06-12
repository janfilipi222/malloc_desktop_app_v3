import ttkbootstrap as tb
from ttkbootstrap.constants import *
import math

class LoadingCircle:
    def __init__(self, parent, size=100, width=5, color="skyblue", speed=5):
        self.parent = parent
        self.size = size
        self.width = width
        self.color = color
        self.speed = speed  # degrees per frame
        self.canvas = tb.Canvas(parent, width=size, height=size, bg=parent.cget("bg"), highlightthickness=0)
        self.canvas.pack()
        
        self.arc = self.canvas.create_arc(
            width/2, width/2, size-width/2, size-width/2,
            start=0, extent=90, style="arc", width=self.width, outline=self.color
        )
        
        self.start_angle = 0
        self.extent = 90
        self.direction = 1
        self._animate()
    
    def _animate(self):
        # Rotace
        self.start_angle = (self.start_angle + self.speed) % 360
        
        # Dynamické prodlužování/krácení oblouku
        self.extent += self.direction * 2
        if self.extent > 270 or self.extent < 60:
            self.direction *= -1
        
        self.canvas.itemconfig(self.arc, start=self.start_angle, extent=self.extent)
        self.parent.after(30, self._animate)  # animace každých 30ms

# Ukázka použití
root = tb.Window(themename="darkly")
root.title("Loading Circle Example")

spinner = LoadingCircle(root, size=120, width=8, color="lightgreen", speed=8)

root.mainloop()
