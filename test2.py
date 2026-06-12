# presentation layer / ui/main_window.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *

app = tb.Window(themename="darkly")
app.title("Notebook demo")
app.geometry("500x300")

notebook = tb.Notebook(app)
notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

# Tab 1
tab1 = tb.Frame(notebook)
notebook.add(tab1, text="První")

tb.Label(tab1, text="Obsah první záložky").pack(pady=20)

# Tab 2
tab2 = tb.Frame(notebook)
notebook.add(tab2, text="Druhá")

tb.Button(tab2, text="Klikni").pack(pady=20)

# Tab 3
tab3 = tb.Frame(notebook)
notebook.add(tab3, text="Třetí")

tb.Entry(tab3).pack(pady=20)

app.mainloop()