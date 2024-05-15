from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, Shader, ClockObject, Vec3, LMatrix4f

from defferedRenderer import DefferedRenderer
from mapGenerator import MapGenerator
from camera import CameraController


map_size = (16, 16, 6)


class Application(ShowBase):
    def __init__(self):
        loadPrcFile("config/config.prc")

        super().__init__()

        print(f"Driver Version: {self.win.getGsg().getDriverVersion()}")

        self.win_width = self.win.getXSize()
        self.win_height = self.win.getYSize()

        render_resolution = (self.win_width, self.win_height)
        #render_resolution = (self.win_width // 2, self.win_height // 2)

        self.deffered_renderer = DefferedRenderer(self, map_size, render_resolution)

        camera_controller = CameraController(self)
        self.camLens.setFov(90)
        self.camLens.setNearFar(0.1, 1000)

        self.globalClock = ClockObject().getGlobalClock()
        self.taskMgr.add(self.update, "update")

        self.time = 0.0

        self.frames_since_clear = 0
        self.cam_previous_pos = self.cam.getPos(self.render)
        self.cam_previous_rot = self.cam.getHpr(self.render)

        main_shader = Shader.load(Shader.SL_GLSL,
                     vertex="shaders/main_vert.glsl",
                     fragment="shaders/main_frag.glsl")
        
        self.main_map = MapGenerator(self, main_shader, map_size)

        self.main_map.node_path.setShaderInput("renderResolution", render_resolution)

        # Weird method for getting the world to apiview matrix
        self.view_rotation_mat = LMatrix4f.rotateMat(-90, Vec3(1.0, 0.0, 0.0))
        self.prev_view_mat = self.render.getMat(self.cam) * self.view_rotation_mat

    
    def update(self, task):
        dt = self.globalClock.dt
        self.time += dt

        self.frames_since_clear += 1
        if self.cam_previous_pos != self.cam.getPos(self.render) or self.cam_previous_rot != self.cam.getHpr(self.render):
            self.frames_since_clear = 0

        self.cam_previous_pos = self.cam.getPos(self.render)
        self.cam_previous_rot = self.cam.getHpr(self.render)

        self.deffered_renderer.deffered_stage0.setShaderInput("cameraPos", self.cam.getPos(self.render))
        self.deffered_renderer.deffered_stage0.setShaderInput("time", self.time)
        self.deffered_renderer.deffered_stage0.setShaderInput("framesSinceClear", self.frames_since_clear)
        
        self.main_map.node_path.setShaderInput("gameTime", self.time)
        
        self.main_map.node_path.setShaderInput("viewMatrix", self.prev_view_mat)
        self.prev_view_mat = self.render.getMat(self.cam) * self.view_rotation_mat

        return task.cont


if __name__ == "__main__":
    app = Application()
    app.run()