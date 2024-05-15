#version 460

in vec3 fragPos;
in vec3 normal;
in vec2 uv;
in vec4 color;

in vec4 curClipPos;
in vec4 prevClipPos;

layout (location = 0) out vec4 gAlbedo;
layout (location = 1) out vec4 gNormal;
layout (location = 2) out vec4 gPosition;
layout (location = 3) out vec4 gVelocity;

uniform sampler2D p3d_Texture0;

void main()
{
    gAlbedo = texture(p3d_Texture0, uv) * vec4(color.rgb, 1.0);
    gAlbedo.a = round(gAlbedo.a);
    
    gNormal = vec4(normal, 1.0);
    gPosition = vec4(fragPos, color.w);

    gVelocity.rgb = (prevClipPos.xyz / prevClipPos.w) - (curClipPos.xyz / curClipPos.w);
    gVelocity.a = 1.0;
}