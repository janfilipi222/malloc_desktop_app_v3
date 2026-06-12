from presentation.main_view import MainView
from presentation.main_view_model import MainViewModel
from data.serial.serial_client import SerialClient
from data.serial.serial_connection_manager import SerialConnectionManager
from domain.communication.command_client import CommandClient
from pathlib import Path
from app.app_context import AppContext
from domain.gcode.gcode_loader import GCodeLoader
from domain.gcode.gcode_parser import GCodeParser
from domain.camera.camera_service import CameraService
from domain.camera.manual_brightness_detector import ManualBrightnessDetector

def main():

    base_dir = Path(__file__).resolve().parent

    context = AppContext(base_dir)

    manager = SerialConnectionManager()
    ser_client = SerialClient(manager)
    com_client = CommandClient(ser_client)
    loader = GCodeLoader()
    parser = GCodeParser()

    cam = CameraService()
    detector = ManualBrightnessDetector(
        min_area=500,
        max_area=3500
    )

    vm = MainViewModel(ser_client, com_client, context, loader, parser, cam, detector)

    app = MainView(vm=vm)
    app.run()




if __name__ == "__main__":
    main()