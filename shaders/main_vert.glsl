#version 460

#define TAA_JITTER_AMOUNT 2.0


in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Color;

out vec3 fragPos;
out vec3 normal;
out vec2 uv;
out vec4 color;

out vec4 curClipPos;
out vec4 prevClipPos;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelMatrixInverseTranspose;

uniform mat4 viewMatrix;

uniform vec2 renderResolution;
uniform float gameTime;

float randomValue(vec2 co)
{
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    //gl_Position.x += (randomValue(fract(gameTime * 34.63).xx) - 0.5) * (1.0 / renderResolution.x) * TAA_JITTER_AMOUNT * gl_Position.w;
	//gl_Position.y += (randomValue(fract(gameTime * 23.33).xx) - 0.5) * (1.0 / renderResolution.y) * TAA_JITTER_AMOUNT * gl_Position.w;

    curClipPos = gl_Position;
    prevClipPos = p3d_ProjectionMatrix * viewMatrix * p3d_ModelMatrix * p3d_Vertex;

    fragPos = vec3(p3d_ModelMatrix * p3d_Vertex);
    normal = p3d_Normal * mat3(p3d_ModelMatrixInverseTranspose);
    uv = p3d_MultiTexCoord0;
    color = p3d_Color;
}