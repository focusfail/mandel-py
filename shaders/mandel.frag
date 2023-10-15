#version 440

out vec4 fragColor;

uniform vec2 screen;
uniform dvec2 center;
lowp uniform double scale;
uniform int max_iter;

const double ratio = screen.x / screen.y;

vec3 smoothGradient(float t) {
    vec3 color1 = vec3(0.0, 0.0, 0.0);
    vec3 color2 = vec3(0.0, 0.5, 1.0);
    vec3 color3 = vec3(1.0, 0.8, 0.0);
    vec3 color4 = vec3(0.9, 0.0, 0.0);

    vec3 color;
    if (t < 0.25) {
        color = mix(color1, color2, t * 4.0);
    } else if (t < 0.5) {
        color = mix(color2, color3, (t - 0.25) * 4.0);
    } else if (t < 0.75) {
        color = mix(color3, color4, (t - 0.5) * 4.0);
    } else {
        color = mix(color4, color1, (t - 0.75) * 4.0);
    }
    return color;
}

void main() {
    double x0, y0, x2, y2;
    double x, y = 0.0;
    float i;

    x0 = (gl_FragCoord.x / screen.x - 0.5) * scale + center.x;
    y0 = (gl_FragCoord.y / screen.y - 0.5) * scale / ratio + center.y;

    while (((y2 + x2) <= 1<<8) && (i < max_iter)) {
        y = 2 * x * y + y0;
        x = x2 - y2 + x0;
        x2 = x * x;
        y2 = y * y;
        i++;
    }

    vec3 c1 = i >= max_iter ? vec3(0.0) : smoothGradient(float(i) / float(max_iter));
    fragColor = vec4(c1, 1.0);
}
