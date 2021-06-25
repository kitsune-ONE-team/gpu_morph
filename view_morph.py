import json
import os
import struct

from panda3d.core import GeomEnums, Texture, TextureStage, Shader, ShaderAttrib

from direct.showbase import ShowBase
from direct.actor.Actor import Actor

from gltf import converter
from gltf.converter import Converter, GltfSettings


# emulate missing M_emission

class VTextureStage(object):
    M_emission = TextureStage.M_modulate
    M_modulate = TextureStage.M_modulate
    M_normal = TextureStage.M_normal
    M_selector = TextureStage.M_selector

    def __new__(cls, *args, **kwargs):
        return TextureStage(*args, **kwargs)


converter.TextureStage = VTextureStage


base = ShowBase.ShowBase()

gltf_data = {}
gltf_buf = None

with open('cube.glb', 'rb') as f:
    assert f.read(4) == b'glTF'  # header
    assert struct.unpack('<I', f.read(4))[0] == 2  # version
    full_size = struct.unpack('<I', f.read(4))

    while True:
        chunk_size = struct.unpack('<I', f.read(4))[0]
        chunk_type = f.read(4)
        chunk_data = f.read(chunk_size)
        if chunk_type == b'JSON':
            gltf_data = json.loads(chunk_data)
        elif chunk_type == b'BIN\000':
            gltf_buf = chunk_data

        if gltf_data and gltf_buf:
            break

settings = GltfSettings(physics_engine='bullet')
converter = Converter(indir=os.getcwd(), outdir=os.getcwd(), settings=settings)
converter.buffers[0] = gltf_buf
converter.update(gltf_data, writing_bam=False)

shader = Shader.load(Shader.SLGLSL, 'morph_v.glsl', 'morph_f.glsl')

model = Actor(converter.active_scene.find('**/+Character'))
model.reparentTo(base.render)
model.setShader(shader)

attr = ShaderAttrib.make(shader)
attr = attr.setFlag(ShaderAttrib.F_hardware_skinning, True)
model.setAttrib(attr)

for gltf_node in gltf_data['nodes']:
    if gltf_node['name'] == 'Cube':
        gltf_mesh = gltf_data['meshes'][gltf_node['mesh']]
        gltf_target = gltf_mesh['primitives'][0]['targets'][0]

        a = gltf_data['accessors'][gltf_target['POSITION']]
        v = gltf_data['bufferViews'][a['bufferView']]
        data = gltf_buf[v['byteOffset']:v['byteOffset'] + v['byteLength']]

        tex = Texture('texbuffer')
        vertex_num = len(data) // 3 // 4  # vec3 of 4-byte float
        tex.setup_buffer_texture(
            vertex_num, Texture.T_float, Texture.F_rgb32, GeomEnums.UH_static)

        image = memoryview(tex.modify_ram_image())
        image[:] = data

        print(bytes(image))

        model.set_shader_input('morph1', tex)

base.run()
