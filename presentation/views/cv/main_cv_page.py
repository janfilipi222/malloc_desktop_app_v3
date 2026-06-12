import ttkbootstrap as ttk
from presentation.main_view_model import MainViewModel
from domain.model.actions.ui_actions import *
from presentation.main_view_model import MainViewModel
from PIL import Image, ImageTk


class MainCVPage(ttk.Frame):
    def __init__(self, parent, on_ui_action, vm: MainViewModel):
        super().__init__(parent)

        self._on_ui_action = on_ui_action
        self._vm = vm

        self.columnconfigure((0, 2), weight=1)
        self.rowconfigure(1, weight=1, minsize=600)

        self._build_ui()

        self._update_frame()

        self._state = False
        self.box_list = []
        self.calib_index = 0
        self.is_calib = False
        self.calib_offsets = [0, 0, 0, 0]

    def _build_ui(self):

        f1 = ttk.Frame(self)
        f1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        f2 = ttk.Frame(self)
        f2.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.canvas1 = ttk.Canvas(f1, width=640, height=480)
        self.img_id1 = self.canvas1.create_image(0, 0, anchor="nw")
        self.canvas1.place(relx=0.5, rely=0.5, anchor="s")
        self.canvas1.config(bg="black")

        self.cord_label = ttk.Label(f1, text="reanocm textx")
        self.cord_label.place(relx=0.5, rely=0.5, anchor="center")

        self.canvas1.bind("<Motion>", self._on_canvas_move)
        self.canvas1.bind("<Button-1>", self._handle_calib)

        self.canvas2 = ttk.Canvas(f2, width=640, height=480)
        self.img_id2 = self.canvas2.create_image(0, 0, anchor="nw")
        self.canvas2.place(relx=0.5, rely=0.5, anchor="s")
        self.canvas2.config(bg="black")

        
        self.brightness_slider = ttk.Scale(self, from_=0, to=255, orient="vertical", length=200)
        self.brightness_slider.grid(row=1, column=1, sticky="ewn", pady=(100, 0))
        self.brightness_slider.config(command=lambda i: self._on_ui_action(OnChangeBrightnessThreshold(i)))

        
        self.top_frame = ttk.Frame(self)
        self.top_frame.grid(column=0, columnspan=3, row=0, sticky="nsew", padx=(110, 0), pady=30)

        self.count_text = ttk.Label(self.top_frame, text="Box count:")
        self.count_text.pack(side="left", padx=50)

        self.btn_go = ttk.Button(self.top_frame, text="Set cords", 
                                 command=lambda: self._on_ui_action(OnCVCordsSet(self.box_list)))
        self.btn_go.pack(side="left", padx=20)

        self.btn_start = ttk.Button(self.top_frame, text="start", 
                                    command=self._handle_start)
        self.btn_start.pack(side="left", padx=20)

        self.btn_stop = ttk.Button(self.top_frame, text="stop", 
                                   command=self._handle_stop)
        self.btn_stop.pack(side="left", padx=20)

        self.btn_calib = ttk.Button(self.top_frame, text="calib", command=self._start_calib)
        self.btn_calib.pack(side="left")

        self.calib_label = ttk.Label(self.top_frame)
        self.calib_label.pack(side="left", padx=20)

    def _start_calib(self):
        # print("start calib")
        self.calib_index = 0
        self.is_calib = True
        self.calib_label.config(text="set left")


    def _handle_calib(self, e):
        # print("handle calib")

        if self.is_calib:
            match self.calib_index:
                case 0:
                    self.calib_offsets[self.calib_index] = self.x
                    self.calib_label.config(text="set right")
                case 1:
                    self.calib_offsets[self.calib_index] = self.x
                    self.calib_label.config(text="set top")
                case 2:
                    self.calib_offsets[self.calib_index] = self.y
                    self.calib_label.config(text="set bottom")
                case 3:
                    self.calib_offsets[self.calib_index] = self.y
                    self.calib_label.config(text="")


            self.calib_index += 1

            if self.calib_index > 3:
                self.is_calib = False
                print(self.calib_offsets)
                self._on_ui_action(OnCamOffsetSet(self.calib_offsets))


    def _on_canvas_move(self, e):
        self.x, self.y = e.x, e.y
        text = f"x: {self.x}   y: {self.y}" 
        self.cord_label.config(text=text)
        

    def _handle_start(self):
        self._state = True
        self._on_ui_action(OnStartRecording())

    def _handle_stop(self): 
        self._state = False

        black = Image.new("RGB", (640, 480), "black")
        photo = ImageTk.PhotoImage(black)

        self.canvas1.itemconfig(self.img_id1, image=photo)
        self.canvas1.image = photo
        self.canvas2.itemconfig(self.img_id2, image=photo)
        self.canvas2.image = photo

        self._on_ui_action(OnStopRecording())

    def _update_frame(self):
        value = self._vm.get_cam_frame()
        if value is not None:
            list, mask, output = value
            self.box_list = list

            self.count_text.config(text=f"Box count: {len(list)}")

            img_mask = Image.fromarray(mask)
            img_output = Image.fromarray(output)

            photo_mask = ImageTk.PhotoImage(img_mask)
            photo_output = ImageTk.PhotoImage(img_output)


            if self._state:
                self.canvas1.itemconfig(self.img_id1, image=photo_output)
                self.canvas2.itemconfig(self.img_id2, image=photo_mask)

                self.canvas1.image = photo_output
                self.canvas2.image = photo_mask

        self.after(15, self._update_frame)