//GLSL
#version 330

in vec4 index;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

in vec4 transform_weight;
in uvec4 transform_index;

uniform mat4 p3d_TransformTable[100];
uniform mat3 p3d_NormalMatrix;

in vec3 p3d_Normal;
in vec3 p3d_Tangent;
in vec3 p3d_Binormal;

uniform samplerBuffer morph1;
uniform mat4 p3d_ModelViewProjectionMatrix;

out vec2 uv;
out vec3 normal;
out vec3 tangent;
out vec3 binormal;

void main()
    {
    //morphs
    int nIndex = int(index.x);
    vec4 offset = texelFetch(morph1, nIndex);
    offset.w = 0.0;
    vec4 vert = p3d_Vertex - offset;
    //hardware skinning
    mat4 matrix = p3d_TransformTable[transform_index.x] * transform_weight.x
              + p3d_TransformTable[transform_index.y] * transform_weight.y
              + p3d_TransformTable[transform_index.z] * transform_weight.z
              + p3d_TransformTable[transform_index.w] * transform_weight.w;

    gl_Position = p3d_ModelViewProjectionMatrix * matrix * vert;

    uv = p3d_MultiTexCoord0.xy;
    mat3 normalMatrix = p3d_NormalMatrix*mat3(matrix);
    normal = normalMatrix * p3d_Normal;
    tangent = normalMatrix * p3d_Tangent;
    binormal = normalMatrix* -p3d_Binormal;
    }
