import tomllib
from decimal import Decimal
from pathlib import Path

import imgui
import moderngl_window as mglw
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.resources.programs import ProgramDescription

with open("conf.toml", "rb") as bf:
    conf = tomllib.load(bf)

# config
MAX_ITER: int = conf["constants"]["max_iterations"]
SHADER_PATH: str = conf["resources"]["rel_shader_path"]
RESOURCE_PATH: str = conf["resources"]["rel_resource_path"]


class Win(mglw.WindowConfig):
    # context settings
    gl_version = (4, 4)
    window_size = (800, 600)
    aspect_ratio = 800 / 600
    resizable = False
    resource_dir = (Path(__file__).parent / RESOURCE_PATH).resolve()
    vsync = False

    # noinspection PyTypeChecker
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        imgui.create_context()
        self.wnd.ctx.error
        self.imgui = ModernglWindowRenderer(self.wnd)

        self.ctx.enable_only(self.ctx.NOTHING)
        self.wnd.title = "Mandelbrot"

        attribs = mglw.geometry.attributes.AttributeNames(
            position="in_vert", normal=False
        )
        self.quad = mglw.geometry.quad_fs(attr_names=attribs)

        self.prog = self.__load_program()
        self.center = [Decimal(0), Decimal(0)]
        self.scale = Decimal(1.0)

        self.auto_zoom = False
        self.zoom_speed = Decimal(1.0)

        self.wnd.mouse_exclusivity = False
        self.wnd.cursor = True

        self.fps = 0

    def render(self, time, frametime):
        self.wnd.ctx.clear(1.0, 0.0, 0.0)

        if self.auto_zoom and self.scale > 1.925641750805661457150236734e-15:
            self.scale -= self.zoom_speed / (10 / self.scale)

        self.prog["max_iter"].value = MAX_ITER
        self.prog["scale"].value = self.scale
        self.prog["center"].value = self.center
        self.prog["screen"].value = self.wnd.size

        if not hasattr(self, "prev_time"):
            self.prev_time = time
            self.frames = 0
        else:
            self.frames += 1
            if time - self.prev_time >= 1.0:
                self.fps = self.frames / (time - self.prev_time)
                self.prev_time = time
                self.frames = 0

        self.quad.render(self.prog)
        self.ui()

    def ui(self):
        imgui.new_frame()

        imgui.set_next_window_size(200, 200)
        imgui.begin("Info")
        imgui.text("Toggle cursor: <mouse3>")
        imgui.text(f"y: {self.center[1]:.12f}")
        imgui.text(f"x: {self.center[0]:.12f}")
        imgui.text(f"FPS: {self.fps:.4f}")

        if imgui.collapsing_header("Zoom")[0]:
            imgui.text("toggle: <g>")
            imgui.text("reset: <r>")
            self.zoom_speed = Decimal(
                imgui.slider_float(
                    "Speed", self.zoom_speed, min_value=0.1, max_value=2.0
                )[1]
            )

        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def mouse_press_event(self, x: int, y: int, button: int):
        self.imgui.mouse_press_event(x, y, button)
        if button == self.wnd.mouse.middle:
            self.wnd.mouse_exclusivity = not self.wnd.mouse_exclusivity

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_position_event(self, x: int, y: int, dx: int, dy: int):
        self.imgui.mouse_position_event(x, y, dx, dy)
        if self.wnd.mouse_exclusivity:
            self.center[0] += Decimal(dx) / (200 / self.scale)
            self.center[1] -= Decimal(dy) / (200 / self.scale)

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        self.imgui.mouse_scroll_event(x_offset, y_offset)
        if (
            self.wnd.mouse_exclusivity
            and self.scale > 1.925641750805661457150236734e-15
        ):
            self.scale -= (self.zoom_speed / (10 / self.scale)) * Decimal(y_offset)

    def key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)
        if action == self.wnd.keys.ACTION_PRESS:  # Check for key press event
            if key == self.wnd.keys.ESCAPE:  # Check for ESC key
                self.close()

            if key == self.wnd.keys.G:
                self.auto_zoom = not self.auto_zoom

            if key == self.wnd.keys.R:
                self.auto_zoom = False
                self.scale = Decimal(1.0)

    @staticmethod
    def __load_program(name: str = "mandel"):
        mglw.resources.register_program_dir(Path(SHADER_PATH).absolute())
        program = mglw.resources.programs.load(
            ProgramDescription(
                vertex_shader=f"{name}.vert", fragment_shader=f"{name}.frag"
            )
        )

        return program

