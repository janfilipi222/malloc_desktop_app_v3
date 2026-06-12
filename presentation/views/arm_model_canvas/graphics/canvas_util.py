import ttkbootstrap as ttk


def draw_rounded_border(
    canvas: ttk.Canvas,
    x1, y1, x2, y2,
    radius=20,
    width=2,
    outline="black"
):

    if radius * 2 > (x2 - x1) or radius * 2 > (y2 - y1):
        raise ValueError("radius is too large")

    # corners (arcs)
    canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius,
                    start=90, extent=90, style="arc",
                    outline=outline, width=width)

    canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius,
                    start=0, extent=90, style="arc",
                    outline=outline, width=width)

    canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2,
                    start=270, extent=90, style="arc",
                    outline=outline, width=width)

    canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2,
                    start=180, extent=90, style="arc",
                    outline=outline, width=width)

    # edges
    canvas.create_line(x1 + radius, y1, x2 - radius, y1,
                    fill=outline, width=width)

    canvas.create_line(x2, y1 + radius, x2, y2 - radius,
                    fill=outline, width=width)

    canvas.create_line(x2 - radius, y2, x1 + radius, y2,
                    fill=outline, width=width)

    canvas.create_line(x1, y2 - radius, x1, y1 + radius,
                    fill=outline, width=width)









