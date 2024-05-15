from panda3d.core import WindowProperties, FrameBufferProperties, GraphicsPipe, GraphicsOutput, CardMaker, NodePath, Camera, OrthographicLens


deffered_stage_cams = []


class DefferedStage(NodePath):
    def __init__(self, base, textures, resolution, rgba_bits = (8, 8, 8, 8), depth_bits = 8, clear_color = (1.0, 0.0, 1.0, 1.0), clear_depth = True, last_stage = False):
        self.base = base
        self.last_stage = last_stage
        
        self.num_textures = len(textures)
        self.stage_index = len(deffered_stage_cams)
        
        
        # start buffer creation ======================
        self.win_prop = WindowProperties(size = resolution)

        self.fb_prop = FrameBufferProperties()
        #self.fb_prop.setBackBuffers(0)
        self.fb_prop.setRgbColor(1)
        self.fb_prop.setRgbaBits(rgba_bits[0], rgba_bits[1], rgba_bits[2], rgba_bits[3])
        self.fb_prop.setDepthBits(depth_bits)
        self.fb_prop.setAuxRgba(self.num_textures - 1)


        self.buffer = self.base.graphicsEngine.makeOutput(self.base.pipe, f"deffered buffer {self.stage_index}", -100 + self.stage_index, self.fb_prop, self.win_prop, GraphicsPipe.BFRefuseWindow | GraphicsPipe.BFResizeable, self.base.win.getGsg(), self.base.win)

        self.buffer.addRenderTexture(textures[0], GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_color)
        if (self.num_textures >= 2):
            self.buffer.addRenderTexture(textures[1], GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_aux_rgba_0)
        if (self.num_textures >= 3):
            self.buffer.addRenderTexture(textures[2], GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_aux_rgba_1)
        if (self.num_textures >= 4):
            self.buffer.addRenderTexture(textures[3], GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_aux_rgba_2)
        if (self.num_textures >= 5):
            self.buffer.addRenderTexture(textures[4], GraphicsOutput.RTM_bind_or_copy, GraphicsOutput.RTP_aux_rgba_3)

        self.buffer.disableClears()

        # end buffer creation =======================


        card_maker = CardMaker("deffered quad")
        card_maker.setFrameFullscreenQuad()

        super().__init__(card_maker.generate())

        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setColor(1, 0.5, 0.5, 1)

        quad_camera = Camera("deffered camera")
        cam_lens = OrthographicLens()
        cam_lens.setFilmSize(2, 2)
        cam_lens.setFilmOffset(0, 0)
        cam_lens.setNearFar(-1, 1)
        quad_camera.setLens(cam_lens)
        quad_camera_np = self.attachNewNode(quad_camera)


        if clear_depth:
            self.buffer.setClearActive(GraphicsOutput.RTP_depth, True)
            self.buffer.setClearValue(GraphicsOutput.RTP_depth, 1.0)

        if clear_color:
            self.buffer.setClearActive(GraphicsOutput.RTP_color, True)
            self.buffer.setClearValue(GraphicsOutput.RTP_color, clear_color)

            if (self.num_textures >= 2):
                self.buffer.setClearActive(GraphicsOutput.RTP_aux_rgba_0, True)
                self.buffer.setClearValue(GraphicsOutput.RTP_aux_rgba_0, (0.0, 0.0, 0.0, 1.0))

            if (self.num_textures >= 3):
                self.buffer.setClearActive(GraphicsOutput.RTP_aux_rgba_1, True)
                self.buffer.setClearValue(GraphicsOutput.RTP_aux_rgba_1, (0.0, 0.0, 0.0, 1.0))

            if (self.num_textures >= 4):
                self.buffer.setClearActive(GraphicsOutput.RTP_aux_rgba_2, True)
                self.buffer.setClearValue(GraphicsOutput.RTP_aux_rgba_2, (0.0, 0.0, 0.0, 1.0))
            
            if (self.num_textures >= 5):
                self.buffer.setClearActive(GraphicsOutput.RTP_aux_rgba_3, True)
                self.buffer.setClearValue(GraphicsOutput.RTP_aux_rgba_3, (0.0, 0.0, 0.0, 1.0))


        if self.last_stage:
            main_display_region = None
            for dr in self.base.win.getDisplayRegions():
                if dr.getCamera() == self.base.cam:
                    main_display_region = dr

            main_display_region.setCamera(quad_camera_np)
            
            main_display_region.disableClears()
            self.base.win.disableClears()


        self.display_region = self.buffer.makeDisplayRegion()
        self.display_region.disableClears()
        self.display_region.setActive(True)
        self.display_region.setScissorEnabled(False)
        if (self.stage_index == 0):
            self.display_region.setCamera(self.base.cam)
        else:
            self.display_region.setCamera(deffered_stage_cams[-1])

        deffered_stage_cams.append(quad_camera_np)