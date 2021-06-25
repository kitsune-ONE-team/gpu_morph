//GLSL
#version 330


uniform sampler2D p3d_Texture0; //color
uniform sampler2D p3d_Texture1; //normal

in vec2 uv;
in vec3 normal;
in vec3 tangent;
in vec3 binormal;

void main()
    {
    vec4 color_map =texture(p3d_Texture0, uv);
    vec4 color=vec4( 0.1, 0.1, 0.1, 1.0);
    gl_FragColor=vec4(color_map.rgb * color.rgb, color_map.a);
    }
