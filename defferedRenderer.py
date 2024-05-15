from panda3d.core import Texture, WindowProperties, FrameBufferProperties, GraphicsPipe, GraphicsOutput, CardMaker, NodePath
from panda3d.core import Camera, OrthographicLens, Shader, Vec2, SamplerState, TransparencyAttrib, Vec3

from defferedStage import DefferedStage

class DefferedRenderer:
    def __init__(self, base, map_size, render_resolution):
        self.base = base
        self.deffered_stage_cams = []


        # The default texture filter type for each of the texture buffers
        textures_filter = SamplerState()
        textures_filter.setMagfilter(SamplerState.FT_linear)
        textures_filter.setMinfilter(SamplerState.FT_linear)
        textures_filter.setWrapU(Texture.WM_border_color)
        textures_filter.setWrapV(Texture.WM_border_color)
        textures_filter.setBorderColor((0.0, 0.0, 0.0, 1.0))


        self.textures_stage0 = [Texture(), Texture(), Texture(), Texture()]
        self.textures_stage0[0].setDefaultSampler(textures_filter)
        self.textures_stage0[1].setDefaultSampler(textures_filter)
        self.textures_stage0[2].setDefaultSampler(textures_filter)
        self.textures_stage0[3].setDefaultSampler(textures_filter)
        self.deffered_stage0 = DefferedStage(base, self.textures_stage0, resolution = render_resolution, rgba_bits = (32, 32, 32, 8), clear_color = (0.5, 0.5, 0.5, 0.5), clear_depth = True)

        self.textures_stage1 = [Texture(), Texture(), Texture()]
        self.textures_stage1[0].setDefaultSampler(textures_filter)
        self.textures_stage1[1].setDefaultSampler(textures_filter)
        self.textures_stage1[2].setDefaultSampler(textures_filter)
        self.deffered_stage1 = DefferedStage(base, self.textures_stage1, resolution = render_resolution, rgba_bits = (32, 32, 32, 8), clear_color = None, clear_depth = False)

        self.textures_stage2 = [Texture(), Texture(), Texture()]
        self.textures_stage2[0].setDefaultSampler(textures_filter)
        self.textures_stage2[1].setDefaultSampler(textures_filter)
        self.textures_stage2[2].setDefaultSampler(textures_filter)
        self.deffered_stage2 = DefferedStage(base, self.textures_stage2, resolution = render_resolution, rgba_bits = (32, 32, 32, 8), clear_color = None, clear_depth = False, last_stage = True)


        # deffered stage 0 ===================================================================================

        quad_shader_stage0 = Shader.load(Shader.SL_GLSL,
                     vertex="shaders/deffered_vert.glsl",
                     fragment="shaders/deffered0_frag.glsl")
        
        self.deffered_stage0.setShader(quad_shader_stage0)
        self.deffered_stage0.setShaderInput("textureRatio", Vec2(render_resolution[0] / self.textures_stage0[0].getXSize(), render_resolution[1] / self.textures_stage0[0].getYSize()))
        self.deffered_stage0.setShaderInput("gNormal", self.textures_stage0[1])
        self.deffered_stage0.setShaderInput("gPosition", self.textures_stage0[2])
        self.deffered_stage0.setShaderInput("gVelocity", self.textures_stage0[3])


        # Texture represeting the whole scene
        self.map_tex = Texture()
        self.map_tex.setup3dTexture(z_size = map_size[2])
        self.map_tex.setFormat(Texture.F_rgba)

        self.map_tex.setMagfilter(SamplerState.FT_nearest)
        self.map_tex.setMinfilter(SamplerState.FT_nearest)
        self.map_tex.setWrapU(Texture.WM_border_color)
        self.map_tex.setWrapV(Texture.WM_border_color)
        self.map_tex.setWrapW(Texture.WM_border_color)
        self.map_tex.setBorderColor((1.0, 1.0, 1.0, 0.0))

        self.map_tex.read(fullpath = "map/map_a_z#.bmp", alpha_fullpath = "map/map_e_z#.bmp", primary_file_num_channels = 3, alpha_file_channel = 0, z = 0, n = 0, read_pages = True, read_mipmaps = False)

        # blue noise
        self.blue_noise_tex = base.loader.loadTexture("textures/blue_noise.png", minfilter = SamplerState.FT_nearest, magfilter = SamplerState.FT_nearest)


        self.deffered_stage0.setShaderInput("mapTex", self.map_tex)
        self.deffered_stage0.setShaderInput("blueNoise", self.blue_noise_tex)
        self.deffered_stage0.setShaderInput("mapSize", Vec3(map_size))
        self.deffered_stage0.setShaderInput("renderResolution", Vec2(render_resolution[0], render_resolution[1]))


        # deffered stage 1 ===================================================================================

        quad_shader_stage1 = Shader.load(Shader.SL_GLSL,
                     vertex="shaders/deffered_vert.glsl",
                     fragment="shaders/deffered1_frag.glsl")
        
        self.deffered_stage1.setShader(quad_shader_stage1)
        self.deffered_stage1.setShaderInput("textureRatio", Vec2(render_resolution[0] / self.textures_stage1[0].getXSize(), render_resolution[1] / self.textures_stage1[0].getYSize()))
        self.deffered_stage1.setShaderInput("gAlbedo", self.textures_stage1[0])
        self.deffered_stage1.setShaderInput("gNormal", self.textures_stage1[1])
        self.deffered_stage1.setShaderInput("gPosition", self.textures_stage1[2])


        # deffered stage 2 ===================================================================================

        quad_shader_stage2 = Shader.load(Shader.SL_GLSL,
                     vertex="shaders/deffered_vert.glsl",
                     fragment="shaders/deffered2_frag.glsl")
        
        self.deffered_stage2.setShader(quad_shader_stage2)
        self.deffered_stage2.setShaderInput("textureRatio", Vec2(render_resolution[0] / self.textures_stage2[0].getXSize(), render_resolution[1] / self.textures_stage2[0].getYSize()))
        self.deffered_stage2.setShaderInput("gAlbedo", self.textures_stage2[0])
        # Only for debug:
        #self.deffered_stage2.setShaderInput("gNormal", self.textures_stage2[1])
        #self.deffered_stage2.setShaderInput("gPosition", self.textures_stage2[2])

        # pass previous render to first stage shader
        self.deffered_stage0.setShaderInput("gAlbedoPrev", self.textures_stage2[0])
        self.deffered_stage0.setShaderInput("gNormalPrev", self.textures_stage2[1])
        self.deffered_stage0.setShaderInput("gPositionPrev", self.textures_stage2[2])

        self.deffered_stage2.setShaderInput("gAlbedoRaw", self.textures_stage0[0])
        self.deffered_stage2.setShaderInput("gPositionRaw", self.textures_stage0[2])

        #base.taskMgr.add(self.update, "update deffered")

    def update(self, task):

        return task.cont