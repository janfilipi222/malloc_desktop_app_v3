import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from presentation.views.arm_model_canvas.graphics import *
from presentation.views.arm_model_canvas.graphics._3d_graphics import *
import numpy as np
from presentation.views.arm_model_canvas.graphics.canvas_util import draw_rounded_border
from domain.motion.FK import calculate_FK
from domain.model.arm_model import ArmModel, Vertex, ProjectedVertex, ProjectedEdge, Edge, ProjectedText, Text
from domain.model.arm_model import ArmModel, Joint

class ArmModelCanvas(ttk.Canvas):
    def __init__(self, parent: ttk.Frame, arm_model: ArmModel, height=700, pad_y=20):
        self._width = 600
        self._height = height
        super().__init__(
            parent,
            bg="white",
            width=self._width,
            height=self._height,
        )
        # self.after(5, self._update_height)
        self._pad_y = pad_y

        self._cam_pitch = 0
        self._cam_yaw = 0
        self._mouse_pos = [0, 0]

        self._push_down = 150

        self._cam_dist = 1100

        self.bind("<Configure>", self._redraw)

        # self.bind("<Key-w>", lambda _: self._move_cam("w"))
        # self.bind("<Key-s>", lambda _: self._move_cam("s"))
        # self.bind("<Key-a>", lambda _: self._move_cam("a"))
        # self.bind("<Key-d>", lambda _: self._move_cam("d"))
        # self.bind("<Key-q>", lambda _: self._move_cam("q"))
        # self.bind("<Key-e>", lambda _: self._move_cam("e"))
        self.bind("<Button-1>", self._set_mouse)
        self.bind("<B1-Motion>", self._mouse_drag)
        self.bind("<MouseWheel>", self.on_mousewheel)
        self.focus_set()

        self._arm_model = arm_model

        self._generate_arm()
        self._generate_grid()

    def _update_height(self):
        self._height = self.master.winfo_height()
        # print(self._height)
        if self._height == 1:
            self.after(5, self._update_height)
        else:
            self.config(height=self._height - self._pad_y * 2)
            self._redraw(None)


    def _generate_arm(self):

        points = self._forward_kinematics(self._arm_model)

        self._arm_model.graphical_model.arm_vertices = []
        for p in points:
            x, y, z = p
            self._arm_model.graphical_model.arm_vertices.append(
                Vertex(
                    x, y, z, "#ffae00", 6
                )
            )

        for i in range(len(self._arm_model.joints)):
            self._arm_model.graphical_model.arm_edges.append(
                Edge(i, i + 1, 0, "#11DF90", 6)
            )

    def _update_arm(self):
        points = self._forward_kinematics(self._arm_model)
        for i, p in enumerate(points):
            x, y, z = p
            v = self._arm_model.graphical_model.arm_vertices[i]
            v.x = x
            v.y = y
            v.z = z       


        
    def _forward_kinematics(self, arm_model: ArmModel):
        points = []

        pos = np.array([0.0, 0.0, 0.0])
        R = np.eye(3) 

        points.append(tuple(pos))

        for i, j in enumerate(arm_model.joints):
            
            angle =  j.angle - math.pi / 2 if i == 0 else j.angle

            if j.axis == "x":
                R = R @ rot_x(angle)
            elif j.axis == "y":
                R = R @ rot_y(angle)
            elif j.axis == "z":
                R = R @ rot_z(angle)

            local_dir = np.array([0.0, 1.0, 0.0])

            world_dir = R @ local_dir

            pos = pos + world_dir * j.length


            points.append(tuple(pos))

        return points


    def _generate_grid(self):

        # Grid Vertices
        # color = "gray"
        color = None
        spacing = 50
        radius = 2
        for i in range(-5, 6, 1):
            self._arm_model.graphical_model.bg_vertices.append(
                Vertex(
                    i * spacing,
                    0,
                    -5 * spacing,
                    color,
                    radius
                )
            )
            self._arm_model.graphical_model.bg_vertices.append(
                Vertex(
                    i * spacing,
                    0,
                    +5 * spacing,
                    color,
                    radius
                )
            )

        for i in range(-5, 5, 1):
            self._arm_model.graphical_model.bg_vertices.append(
                Vertex(
                    -5 * spacing,
                    0,
                    i * spacing,
                    color,
                    radius
                )
            )
            self._arm_model.graphical_model.bg_vertices.append(
                Vertex(
                    +5 * spacing,
                    0,
                    i * spacing,
                    color,
                    radius
                )
            )

        # Grid edges
        color = "#3f3f3f"
        radius = 2
        for i in range(0, 42, 2):
            self._arm_model.graphical_model.bg_edges.append(
                Edge(
                    i, i + 1, 0, color, radius
                )
            )
        self._arm_model.graphical_model.bg_edges.append(
                Edge(
                    1, 21, 0, color, radius
                )
            )
        
            
    def on_mousewheel(self, e):
        if e.delta > 0 or getattr(e, "num", None) == 4:
            self._cam_dist -= 20
        else:
            self._cam_dist += 20
        self._redraw(None)

    def _set_mouse(self, e):
        self._mouse_pos[0], self._mouse_pos[1] = e.x, e.y

    def _mouse_drag(self, e):
        mulx = 0.007
        dx = e.x - self._mouse_pos[0]
        dy = e.y - self._mouse_pos[1]
        self._cam_yaw -= dx * mulx
        self._cam_pitch -= dy * mulx
        self._mouse_pos[0], self._mouse_pos[1] = e.x, e.y
        self._redraw(None)

    # def _move_cam(self, dir):
    #     print(dir)
    #     match (dir):
    #         case "a": self._joints[1].angle += math.radians(5)
    #         case "d": self._joints[1].angle -= math.radians(5)
    #         case "w": self._joints[3].angle += math.radians(5)
    #         case "s": self._joints[3].angle -= math.radians(5)
    #         case "q": self._joints[4].angle += math.radians(5)
    #         case "e": self._joints[4].angle -= math.radians(5)

    #     self._update_arm()
    #     self._redraw(None)

    #     print(self._joints[0].angle)



    def _redraw(self, event):

        self.delete("all")
        try:
            draw_rounded_border(
                self,
                0, 0, self.winfo_width(), self.winfo_height(),
                outline="#464646"
            )
        except: pass


        transformed_arm = []
        transformed_bg = []
    
        draw_list = []

        for v in self._arm_model.graphical_model.arm_vertices:
            color = v.color
            radius = v.radius
            v = (v.x, v.y, v.z)
            v = camera_transform(v, self._cam_yaw, self._cam_pitch, self._cam_dist)
            projected = project(v, self._width, self._height)
            v = ProjectedVertex(projected[0], projected[1], v[2], color, radius)
            transformed_arm.append(v)
            draw_list.append((0, v))

        for v in self._arm_model.graphical_model.bg_vertices:
            color = v.color
            radius = v.radius
            v = (v.x, v.y, v.z)
            v = camera_transform(v, self._cam_yaw, self._cam_pitch, self._cam_dist)
            projected = project(v, self._width, self._height)
            v = ProjectedVertex(projected[0], projected[1], v[2], color, radius)
            transformed_bg.append(v)
            draw_list.append((0, v))

        for v in self._arm_model.graphical_model.text_vertices:
            color = v.color
            text = v.text
            v = (v.x, v.y, v.z)
            v = camera_transform(v, self._cam_yaw, self._cam_pitch, self._cam_dist)
            projected = project(v, self._width, self._height)
            v = ProjectedText(projected[0], projected[1], v[2], color, text)
            draw_list.append((2, v))
            
        # trajectory vertices
        for v in self._arm_model.graphical_model.trajectory_vertices:
            color = v.color
            radius = v.radius
            v = (v.x, v.y, v.z)
            v = camera_transform(v, self._cam_yaw, self._cam_pitch, self._cam_dist)
            projected = project(v, self._width, self._height)
            v = ProjectedVertex(projected[0], projected[1], v[2], color, radius)
            draw_list.append((0, v))



        arm_edges = []
        bg_edges = []

        for edge in self._arm_model.graphical_model.arm_edges:
            i1, i2 = edge.v1, edge.v2
            v1 = transformed_arm[i1]
            v2 = transformed_arm[i2]
            # distance = transformed_arm[i1].distance if transformed_arm[i1].distance < transformed_arm[i2].distance else transformed_arm[i2].distance
            distance = (v1.distance + v2.distance) / 2

            draw_list.append((
                1, 
                ProjectedEdge(
                    v1.x,
                    v1.y,
                    v2.x,
                    v2.y,
                    distance,
                    edge.color,
                    edge.width
                )
            ))

        for edge in self._arm_model.graphical_model.bg_edges:
            i1, i2 = edge.v1, edge.v2
            v1 = transformed_bg[i1]
            v2 = transformed_bg[i2]
            # distance = v1.distance if v1.distance < v2.distance else v2.distance
            distance = (v1.distance + v2.distance) / 2
            # distance = (v1.distance + v2.distance)

            draw_list.append((
                1, 
                ProjectedEdge(
                    v1.x,
                    v1.y,
                    v2.x,
                    v2.y,
                    distance,
                    edge.color,
                    edge.width
                )
            ))


        draw_list.sort(reverse=True, key=lambda e: e[1].distance)


        for t in draw_list:
            if t[0] == 0:
                p = t[1]
                if p.color == None:
                    continue
                radius = p.radius * (1000 / p.distance)
                # for p in all_vertices:
                x, y = p.x, p.y
                self.create_oval(
                    x - radius, 
                    y - radius,
                    x + radius,
                    y + radius,
                    fill=p.color,
                    outline=p.color
                ) 

            elif t[0] == 1:
                e = t[1]
                if e.color == None:
                    continue
                # for e in all_edges:
                x1, y1, x2, y2 = e.x1, e.y1, e.x2, e.y2
                width = e.width * 500 / e.distance * 2
                self.create_line(
                    x1, y1, x2, y2,
                    width=width,
                    fill=e.color,
                    smooth=False
                )

            else: 
                e = t[1]
                if e.color == None:
                    continue
                x, y = e.x, e.y
                self.create_text(
                    x, y,
                    text=e.text,
                    fill = e.color,
                    font = ("Arial", 10),
                    anchor="center"
                )

    def update(self):

        # print("\n\nupdate")

        # for i, j in enumerate(self._state.joints):
        #     angle = math.radians(angle)
        #     self._joints[i].angle = angle
        #     print(angle)

        self._update_arm()
        self._redraw(None)


