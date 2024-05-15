#version 460

#define GAMMA 2.2

in vec2 uv;

layout (location = 0) out vec4 fragColor;

uniform sampler2D gAlbedo;
uniform sampler2D gAlbedoRaw;
uniform sampler2D gPositionRaw;
//uniform sampler2D gNormal;
//uniform sampler2D gPosition;


// Narkowicz 2015, "ACES Filmic Tone Mapping Curve"
vec3 ACESFilm(vec3 x)
{
    float a = 2.51;
    float b = 0.03;
    float c = 2.43;
    float d = 0.59;
    float e = 0.14;
    return clamp((x*(a*x+b))/(x*(c*x+d)+e), 0.0, 1.0);
}

void main()
{
    if (texture(gPositionRaw, uv).a < 0.5)
        fragColor = texture(gAlbedo, uv) * texture(gAlbedoRaw, uv);
    else
        fragColor = 2.0 * texture(gAlbedoRaw, uv);
    fragColor.a = 1.0;

    // tonemapping and gamma correction
    fragColor.rgb = ACESFilm(fragColor.rgb);
    fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / GAMMA));

    //fragColor = texture(gPosition, uv) * 0.01;
}