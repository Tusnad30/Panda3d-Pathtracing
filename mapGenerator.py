from panda3d.core import PNMImage, GeomVertexFormat, GeomVertexData, Geom, GeomVertexWriter, GeomTriangles, GeomNode


class MapGenerator():
    def __init__(self, base, main_shader, map_size):

        map_a = [PNMImage() for i in range(map_size[2])]
        for i, img in enumerate(map_a):
            img.read(f"map/map_a_z{i}.bmp")
            img.flip(flip_x = False, flip_y = True, transpose = False)

        map_e = [PNMImage() for i in range(map_size[2])]
        for i, img in enumerate(map_e):
            img.read(f"map/map_e_z{i}.bmp")
            img.flip(flip_x = False, flip_y = True, transpose = False)


        mesh_format = GeomVertexFormat().getV3n3c4t2()
        vertex_data = GeomVertexData("map vertexdata", mesh_format, Geom.UHStatic)

        vertex = GeomVertexWriter(vertex_data, "vertex")
        normal = GeomVertexWriter(vertex_data, "normal")
        texcoord = GeomVertexWriter(vertex_data, "texcoord")
        colors = GeomVertexWriter(vertex_data, "color")

        primitive = GeomTriangles(Geom.UHStatic)


        def getMapBool(x, y, z):
            if x < 0 or x > (map_size[0] - 1) or z < 0 or z > (map_size[2] - 1) or y < 0 or y > (map_size[1] - 1):
                return 1
            elif map_a[z].getXel(x, y) == (0, 0, 0):
                return 0
            
        def getMapVal(x, y, z):
            return map_a[z].getXelA(x, y)
        
        def getMapEmmisive(x, y, z):
            return map_e[z].getRed(x, y)
            

        index_num = 0

        def addPlane(x, y, z, verts, uvs, norm, color, emmisive):
            nonlocal index_num

            vertex.addData3(verts[0][0] + x, verts[0][1] + y, verts[0][2] + z)
            vertex.addData3(verts[1][0] + x, verts[1][1] + y, verts[1][2] + z)
            vertex.addData3(verts[2][0] + x, verts[2][1] + y, verts[2][2] + z)
            vertex.addData3(verts[3][0] + x, verts[3][1] + y, verts[3][2] + z)

            texcoord.addData2(uvs[0])
            texcoord.addData2(uvs[1])
            texcoord.addData2(uvs[2])
            texcoord.addData2(uvs[3])

            normal.addData3(norm)
            normal.addData3(norm)
            normal.addData3(norm)
            normal.addData3(norm)

            colors.addData4(color[0], color[1], color[2], emmisive)
            colors.addData4(color[0], color[1], color[2], emmisive)
            colors.addData4(color[0], color[1], color[2], emmisive)
            colors.addData4(color[0], color[1], color[2], emmisive)

            primitive.addVertices(0 + index_num, 2 + index_num, 1 + index_num)
            primitive.addVertices(2 + index_num, 3 + index_num, 1 + index_num)
            index_num += 4
            

        for z in range(map_size[2]):
            for x in range(map_size[0]):
                for y in range(map_size[1]):
                    if not getMapBool(x, y, z) == 0:
                        cur_color = getMapVal(x, y, z)

                        emmisive = 0
                        if getMapEmmisive(x, y, z) != 0.0:
                            emmisive = 1

                        px = getMapBool(x + 1, y, z)
                        nx = getMapBool(x - 1, y, z)
                        pz = getMapBool(x, y, z + 1)
                        nz = getMapBool(x, y, z - 1)
                        py = getMapBool(x, y + 1, z)
                        ny = getMapBool(x, y - 1, z)

                        if px == 0:
                            addPlane(x, y, z, [(1,0,0), (1,0,1), (1,1,0), (1,1,1)], [(0, 0), (1.0, 0), (0, 1.0), (1.0, 1.0)], (1, 0, 0), cur_color, emmisive)
                        if nx == 0:
                            addPlane(x, y, z, [(0,0,1), (0,0,0), (0,1,1), (0,1,0)], [(0, 0), (1.0, 0), (0, 1.0), (1.0, 1.0)], (-1, 0, 0), cur_color, emmisive)
                        if pz == 0:
                            addPlane(x, y, z, [(1,0,1), (0,0,1), (1,1,1), (0,1,1)], [(0, 0), (1.0, 0), (0, 1.0), (1.0, 1.0)], (0, 0, 1), cur_color, emmisive)
                        if nz == 0:
                            addPlane(x, y, z, [(0,0,0), (1,0,0), (0,1,0), (1,1,0)], [(0, 0), (1.0, 0), (0, 1.0), (1.0, 1.0)], (0, 0, -1), cur_color, emmisive)
                        if py == 0:
                            addPlane(x, y, z, [(0,1,0), (1,1,0), (0,1,1), (1,1,1)], [(0, 0), (1.0, 0), (0, 1.0), (1.0, 1.0)], (0, 1, 0), cur_color, emmisive)
                        if ny == 0:
                            addPlane(x, y, z, [(0,0,1), (1,0,1), (0,0,0), (1,0,0)], [(0, 0), (1.0, 0), (0, 1.0), (1.0, 1.0)], (0, -1, 0), cur_color, emmisive)


        primitive.closePrimitive()

        geometry = Geom(vertex_data)
        geometry.addPrimitive(primitive)

        geom_node = GeomNode("map geomnode")
        geom_node.addGeom(geometry)

        self.node_path = base.render.attachNewNode(geom_node)
        self.node_path.setShader(main_shader)
        self.node_path.reparentTo(base.render)