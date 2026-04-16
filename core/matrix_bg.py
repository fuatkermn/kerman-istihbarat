#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import random

class MatrixBackground:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.font_size = 14
        self.font = ("Courier", self.font_size, "bold")
        self.columns = width // self.font_size
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self.after_id = None
        
    def draw(self):
        self.canvas.delete("matrix")
        for i in range(len(self.drops)):
            if random.random() > 0.5:
                char = chr(random.randint(0x30A0, 0x30FF))
            else:
                char = chr(random.randint(65, 90))
            x = i * self.font_size
            y = self.drops[i] * self.font_size
            green = min(255, 100 + (self.drops[i] % 155))
            color = f'#00{green:02x}00'
            self.canvas.create_text(x, y, text=char, fill=color, font=self.font, anchor="nw", tags="matrix")
            if y > self.height and random.random() > 0.975:
                self.drops[i] = 0
            self.drops[i] += 1
        self.after_id = self.canvas.after(50, self.draw)
    
    def stop(self):
        if self.after_id:
            self.canvas.after_cancel(self.after_id)
