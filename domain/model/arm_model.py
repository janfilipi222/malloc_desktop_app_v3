from dataclasses import dataclass, field


@dataclass(slots=True)
class Vertex:
    x: float
    y: float
    z: float
    color: str
    radius: int

@dataclass(slots=True)
class ProjectedVertex:
    x: float
    y: float
    distance: float
    color: str
    radius: int

@dataclass(slots=True)
class Edge:
    v1: int
    v2: int
    distance: float
    color: str
    width: int

@dataclass(slots=True)
class ProjectedEdge:
    x1: float
    y1: float
    x2: float
    y2: float
    distance: int
    color: str
    width: int

@dataclass(slots=True)
class Text:
    x: float
    y: float
    z: float
    color: str
    text: str

@dataclass(slots=True)
class ProjectedText:
    x: float
    y: float
    distance: float
    color: str
    text: str


@dataclass(slots=True)
class JointHardware:
    steps_per_revolution: int
    gear_ratio: float

@dataclass(slots=True)
class Joint:
    length: float
    axis: str
    angle: float
    min_angle: float
    max_angle: float



@dataclass(slots=True)
class ArmGraphicalModel:
    arm_vertices: list = field(default_factory=list)
    arm_edges: list = field(default_factory=list)

    bg_vertices: list = field(default_factory=list)
    bg_edges: list = field(default_factory=list)

    joint_lengths: tuple = (0, 177, 97)

    color: str = "#979797"

    text_vertices: list = field(default_factory=lambda: [
        Text(0, 0, -300, "#979797", "Front"),
        Text(0, 0, 300, "#979797", "Back"),
        Text(-300, 0, 0, "#979797", "Right"),
        Text(300, 0, 0, "#979797", "Left"),
    ])

    trajectory_vertices: list = field(default_factory=list)


@dataclass(slots=True)
class EEPosition:
    pos: list[float] = field(default_factory=lambda: [0, 0, 0])
    rot: list[float] = field(default_factory=lambda: [0, 0, 0])


@dataclass(slots=True)
class ArmModel:
    joints: tuple[Joint] = (
        Joint(185, "y", 0, -135, 135),
        Joint(177, "z", 0, -30, 89),
        Joint(87, "z", 0, -30, 120),
        Joint(112, "y", 0, -90, 90),
        Joint(72, "z", 0, -90, 90),
        Joint(0, "y", 0, -90, 90)
    )

    ee_position: EEPosition = field(default_factory=lambda: EEPosition([0,0,0], [0,0,0]))
    target_ee_position: EEPosition = field(default_factory=lambda: EEPosition([0,0,0], [0,0,0]))

    hardware: tuple[JointHardware] = (
        JointHardware(3200, 4),
        JointHardware(3200, 25),
        JointHardware(3200, 25),
        JointHardware(200, 20.25),
        JointHardware(200, 32),
        JointHardware(200, 16)
    )

    graphical_model: ArmGraphicalModel = field(
        default_factory=ArmGraphicalModel
    )

