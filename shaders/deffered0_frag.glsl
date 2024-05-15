#version 460

#define RAY_MAXSTEPS 20
#define RAY_MAXDIST 100000.0
#define RAY_SAMPLE_BIAS 0.001

#define RAY_MAXBOUNCES 3
#define RAY_MAXSAMPLES 1

#define MAX_EMISSION_INTENSITY 2.0

#define NOISE_TEX_SIZE 1024.0

#define MAX_HISTORY 200.0


in vec2 uv;

layout (location = 0) out vec4 fragColor;
layout (location = 1) out vec4 gNormalNext;
layout (location = 2) out vec4 gPositionNext;

uniform sampler2D gNormal;
uniform sampler2D gPosition;
uniform sampler2D gVelocity;

uniform sampler2D gAlbedoPrev;
uniform sampler2D gNormalPrev;
uniform sampler2D gPositionPrev;

uniform sampler3D mapTex;

uniform sampler2D blueNoise;

uniform vec3 mapSize;
uniform vec3 cameraPos;
uniform float time;
uniform int framesSinceClear;

uniform int osg_FrameNumber;

uniform vec2 renderResolution;
uniform vec2 textureRatio;


// ==========================================================================================================

float random_seed;

const float noise_texel_size = 1.0 / NOISE_TEX_SIZE;

vec3 randomVector()
{
	float frac = random_seed / NOISE_TEX_SIZE;
	vec2 rand_offs = texture(blueNoise, vec2(frac, int(frac) * noise_texel_size)).ra;

	vec3 rand_tex = texture(blueNoise, (gl_FragCoord.xy / NOISE_TEX_SIZE) + rand_offs).rgb;
	vec3 rand_vec = rand_tex * 2.0 - 1.0;
	random_seed += 1.0;
    return normalize(rand_vec);
}


// ==========================================================================================================


vec4 readMapData(vec3 position)
{
    vec3 uvw = position / mapSize;
    return texture(mapTex, uvw);
}

struct rayHit
{
    int hit;
    vec3 position;
    vec3 normal;
    vec3 color;
    float emissive;
};

rayHit rayIntersect(vec3 origin, vec3 direction)
{
	vec3 sample_bias = direction * RAY_SAMPLE_BIAS;
	
	// X ----------------------------------------------------------------------
	vec3 xray_pos = origin;
	float xray_dist = RAY_MAXDIST;
	vec3 xray_hit = vec3(0.0);
	{
		vec3 initial_step = vec3(0.0);
		vec3 step_size = vec3(0.0);
		int skip = 0;

		if (direction.x == 0.0)
			skip = 1;
		else if (direction.x > 0.0)
		{
			float dx = 1.0 - fract(origin.x);
			initial_step = direction * (dx / direction.x);
			step_size = direction * (1.0 / direction.x);
		}
		else if (direction.x < 0.0)
		{
			float dx = fract(origin.x);
			initial_step = direction * (-dx / direction.x);
			step_size = direction * (-1.0 / direction.x);
		}

		xray_pos += initial_step;
		vec3 hit = readMapData(xray_pos + sample_bias).xyz;
		if (hit != vec3(0.0) && skip == 0)
		{
			xray_dist = distance(xray_pos, origin);
			xray_hit = hit;
			skip = 1;
		}

		if (skip == 0)
		{
			for (int i = 0; i < RAY_MAXSTEPS; i++)
			{
				xray_pos += step_size;
				vec3 hit = readMapData(xray_pos + sample_bias).xyz;
				if (hit != vec3(0.0))
				{
					xray_dist = distance(xray_pos, origin);
					xray_hit = hit;
					break;
				}
			}
		}
	}

	// Y ----------------------------------------------------------------------
	vec3 yray_pos = origin;
	float yray_dist = RAY_MAXDIST;
	vec3 yray_hit = vec3(0.0);
	{
		vec3 initial_step = vec3(0.0);
		vec3 step_size = vec3(0.0);
		int skip = 0;

		if (direction.y == 0.0)
			skip = 1;
		else if (direction.y > 0.0)
		{
			float dy = 1.0 - fract(origin.y);
			initial_step = direction * (dy / direction.y);
			step_size = direction * (1.0 / direction.y);
		}
		else if (direction.y < 0.0)
		{
			float dy = -fract(origin.y);
			initial_step = direction * (dy / direction.y);
			step_size = direction * (-1.0 / direction.y);
		}

		yray_pos += initial_step;
		vec3 hit = readMapData(yray_pos + sample_bias).xyz;
		if (hit != vec3(0.0) && skip == 0)
		{
			yray_dist = distance(yray_pos, origin);
			yray_hit = hit;
			skip = 1;
		}

		if (skip == 0)
		{
			for (int i = 0; i < RAY_MAXSTEPS; i++)
			{
				yray_pos += step_size;
				vec3 hit = readMapData(yray_pos + sample_bias).xyz;
				if (hit != vec3(0.0))
				{
					yray_dist = distance(yray_pos, origin);
					yray_hit = hit;
					break;
				}
			}
		}
	}

	// Z ----------------------------------------------------------------------
	vec3 zray_pos = origin;
	float zray_dist = RAY_MAXDIST;
	vec3 zray_hit = vec3(0.0);
	{
		vec3 initial_step = vec3(0.0);
		vec3 step_size = vec3(0.0);
		int skip = 0;

		if (direction.z == 0.0)
			skip = 1;
		else if (direction.z > 0.0)
		{
			float dz = 1.0 - fract(origin.z);
			initial_step = direction * (dz / direction.z);
			step_size = direction * (1.0 / direction.z);
		}
		else if (direction.z < 0.0)
		{
			float dz = -fract(origin.z);
			initial_step = direction * (dz / direction.z);
			step_size = direction * (-1.0 / direction.z);
		}

		zray_pos += initial_step;
		vec3 hit = readMapData(zray_pos + sample_bias).xyz;
		if (hit != vec3(0.0) && skip == 0)
		{
			zray_dist = distance(zray_pos, origin);
			zray_hit = hit;
			skip = 1;
		}

		if (skip == 0)
		{
			for (int i = 0; i < RAY_MAXSTEPS; i++)
			{
				zray_pos += step_size;
				vec3 hit = readMapData(zray_pos + sample_bias).xyz;
				if (hit != vec3(0.0))
				{
					zray_dist = distance(zray_pos, origin);
					zray_hit = hit;
					break;
				}
			}
		}
	}


	rayHit ray_hit;
	ray_hit.hit = 0;

	if (xray_dist <= yray_dist && xray_dist <= zray_dist && xray_dist != RAY_MAXDIST)
	{
		ray_hit.position = xray_pos;
		ray_hit.color = xray_hit;
		ray_hit.normal = (direction.x > 0.0) ? vec3(-1.0, 0.0, 0.0) : vec3(1.0, 0.0, 0.0);
		ray_hit.hit = 1;
	}
	else if (yray_dist <= xray_dist && yray_dist <= zray_dist && yray_dist != RAY_MAXDIST)
	{
		ray_hit.position = yray_pos;
		ray_hit.color = yray_hit;
		ray_hit.normal = (direction.y > 0.0) ? vec3(0.0, -1.0, 0.0) : vec3(0.0, 1.0, 0.0);
		ray_hit.hit = 1;
	}
	else if (zray_dist <= xray_dist && zray_dist <= yray_dist && zray_dist != RAY_MAXDIST)
	{
		ray_hit.position = zray_pos;
		ray_hit.color = zray_hit;
		ray_hit.normal = (direction.z > 0.0) ? vec3(0.0, 0.0, -1.0) : vec3(0.0, 0.0, 1.0);
		ray_hit.hit = 1;
	}

    ray_hit.emissive = (readMapData(ray_hit.position + sample_bias).a > 0.75) ? 1.0 : 0.0;

	return ray_hit;
}


// ==========================================================================================================


vec3 traceRay(vec3 origin, vec3 normal)
{
    vec3 ray_color = vec3(1.0);
    vec3 ray_incoming_light = vec3(0.0);

	vec3 ray_origin = origin;
    vec3 ray_direction = normalize(normal + randomVector());

    for (int i = 0; i < RAY_MAXBOUNCES; i++)
    {
		rayHit ray_hit = rayIntersect(ray_origin, ray_direction);
        if (ray_hit.hit == 1)
        {
            ray_incoming_light += ray_hit.color * ray_hit.emissive * ray_color * MAX_EMISSION_INTENSITY;
            ray_color *= ray_hit.color;

			ray_origin = ray_hit.position + ray_hit.normal * 0.01;
			ray_direction = normalize(ray_hit.normal + randomVector());
        }
        else break;
		if (ray_incoming_light != vec3(0.0)) break;
    }

    return ray_incoming_light;
}


// ==========================================================================================================


void main()
{
    vec4 g_normal = texture(gNormal, uv);
    vec4 g_position = texture(gPosition, uv);
	vec4 g_velocity = texture(gVelocity, uv);

    vec3 normal = normalize(g_normal.xyz);
    vec3 fragPos = g_position.xyz;

	random_seed = 0.0 + osg_FrameNumber;


	// Pathtracing =====================================

    vec3 total_incoming_light = vec3(0.0);

    if (g_position.xyz != vec3(0.0))
    {
        for (int i = 0; i < RAY_MAXSAMPLES; i++)
        {
            total_incoming_light += traceRay(fragPos + normal * 0.01, normal);
        }

        total_incoming_light /= RAY_MAXSAMPLES;
    }
    else
        total_incoming_light = vec3(1.0);


	// Temporal Denoising ==============================

	vec2 prev_uv = uv + g_velocity.xy * 0.5 * textureRatio;
	vec4 prev_position = texture(gPositionPrev, prev_uv);
	vec3 prev_normal = normalize(texture(gNormalPrev, prev_uv).xyz);

	float history = 0.0;
	vec3 old_render = vec3(0.0);

	if (distance(prev_position.xyz, fragPos) < 0.01 && dot(prev_normal, normal) > 0.5)
	{
		old_render = texture(gAlbedoPrev, prev_uv).rgb;
		history = prev_position.w;
	}

	float weight = 1.0 / (history + 1.0);
	vec3 accumulated_average = old_render * (1.0 - weight) + total_incoming_light * weight;

    fragColor.rgb = accumulated_average;
	fragColor.a = 1.0;

	if (history < MAX_HISTORY)
		history += 1.0;

	gNormalNext = vec4(normal, 1.0);
	gPositionNext = vec4(g_position.xyz, history);
}