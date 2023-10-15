#version 440
layout (location = 0) in vec3 in_vert;


void main() {
    gl_Position = vec4(in_vert, 1.0);
}