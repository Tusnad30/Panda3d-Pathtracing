#version 460

in vec2 uv;

layout (location = 0) out vec4 fragColor;
layout (location = 1) out vec4 gNormalNext;
layout (location = 2) out vec4 gPositionNext;

uniform sampler2D gAlbedo;
uniform sampler2D gNormal;
uniform sampler2D gPosition;

void main()
{
    fragColor.rgb = texture(gAlbedo, uv).rgb;
    fragColor.a = 1.0;
    gNormalNext = texture(gNormal, uv);
    gPositionNext = texture(gPosition, uv);
}