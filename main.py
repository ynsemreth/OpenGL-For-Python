import sys
import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

global shapes
clipping_rectangle = None
clipping_active = False
width, height = 500,500
center = (width / 2, height / 2)
zoom_factor = 1.0
translation_step = 10.0
current_shape_index = 0

class Ston:
    def __init__(self, vertices, draw_function, color=(1.0, 1.0, 1.0)):
        self.vertices = vertices
        self.draw_function = draw_function
        self.color = color
        self.angle = 0.0
    def draw(self, filled=True):
        glPushMatrix()
        glTranslatef(self.vertices[0][0], self.vertices[0][1], 0.0)
        glRotatef(self.angle, 0, 0, 1)
        glTranslatef(-self.vertices[0][0], -self.vertices[0][1], 0.0)
        glColor3f(*self.color)
        self.draw_function(self.vertices)
        glPopMatrix()
    def translate(self, translation_vector):
        self.vertices = [(x + translation_vector[0], y + translation_vector[1]) for x, y in self.vertices]
    def rotate(self, angle_increment=10.0):
        self.angle = (self.angle + angle_increment) % 360.0
def put_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()
def draw_line(vertices, filled=True):
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    if dx > dy:
        steps = int(dx)
    else:
        steps = int(dy)

    x_increment = (x2 - x1) / steps
    y_increment = (y2 - y1) / steps

    x, y = x1, y1

    put_pixel(round(x), round(y))

    for _ in range(steps):
        x += x_increment
        y += y_increment
        put_pixel(round(x), round(y))

def draw_change_line(start_point, end_point):
    x1, y1 = start_point
    x2, y2 = end_point

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    if dx > dy:
        steps = int(dx)
    else:
        steps = int(dy)

    if steps == 0:
        steps = 1

    x_increment = (x2 - x1) / steps
    y_increment = (y2 - y1) / steps

    x, y = x1, y1

    for _ in range(steps):
        x += x_increment
        y += y_increment
        put_pixel(round(x), round(y))

def draw_filled_triangle(vertices):
    min_y = min(vertex[1] for vertex in vertices)
    max_y = max(vertex[1] for vertex in vertices)
    edges = [(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]

    for y in range(int(min_y), int(max_y + 1)):
        intersections = []

        for edge in edges:
            start_vertex, end_vertex = edge
            x1, y1 = start_vertex
            x2, y2 = end_vertex

            if min(y1, y2) <= y <= max(y1, y2):
                x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                intersections.append(x)

        intersections.sort()
        for i in range(0, len(intersections), 2):
            x_start, x_end = intersections[i], intersections[i + 1]
            for x in range(int(x_start), int(x_end + 1)):
                put_pixel(x, y)

def draw_empty_triangle(vertices, filled=True):
    for i in range(3):
        start_vertex = vertices[i]
        end_vertex = vertices[(i + 1) % 3]
        draw_change_line(start_vertex, end_vertex)

def draw_empty_circle(vertices, filled=True):
    cx, cy = vertices[0]
    radius = math.sqrt((vertices[1][0] - cx) ** 2 + (vertices[1][1] - cy) ** 2)

    for i in range(360):
        angle = math.radians(i)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        put_pixel(round(x), round(y))

def draw_filled_circle(vertices):
    cx, cy = vertices[0]
    radius = math.sqrt((vertices[1][0] - cx) ** 2 + (vertices[1][1] - cy) ** 2)
    for y in range(int(cy - radius), int(cy + radius)):
        temp = radius**2 - (y - cy)**2
        if temp < 0:
            temp = 0
        x_start = cx - math.sqrt(temp)
        x_end = cx + math.sqrt(temp)

        for x in range(int(x_start), int(x_end) + 1):
            put_pixel(x, y)

def draw_filled_disk(vertices):
    cx, cy = vertices[0]
    outer_radius = math.sqrt((vertices[1][0] - cx) ** 2 + (vertices[1][1] - cy) ** 2)
    inner_radius = outer_radius / 2

    for y in range(int(cy - outer_radius), int(cy + outer_radius)):
        temp_outer = outer_radius**2 - (y - cy)**2
        temp_inner = inner_radius**2 - (y - cy)**2
        if temp_outer < 0:
            temp_outer = 0
        if temp_inner < 0:
            temp_inner = 0
        x_start_outer = cx - math.sqrt(temp_outer)
        x_end_outer = cx + math.sqrt(temp_outer)
        x_start_inner = cx - math.sqrt(temp_inner)
        x_end_inner = cx + math.sqrt(temp_inner)

        for x in range(int(x_start_outer), int(x_start_inner) + 1):
            put_pixel(x, y)
        for x in range(int(x_end_inner), int(x_end_outer) + 1):
            put_pixel(x, y)
def draw_smooth_curve(vertices, filled=True):
    cx, cy = vertices[0]
    radius = math.sqrt((vertices[1][0] - cx) ** 2 + (vertices[1][1] - cy) ** 2)

    previous_point = None

    for i in range(30, 151):
        angle = math.radians(i)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)

        if previous_point is not None:
            draw_change_line(previous_point, (x, y))

        previous_point = (x, y)

def draw_empty_rectangle(vertices):
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]

    draw_change_line((x1, y1), (x2, y1))
    draw_change_line((x2, y1), (x2, y2))
    draw_change_line((x2, y2), (x1, y2))
    draw_change_line((x1, y2), (x1, y1))

def draw_filled_rectangle(vertices):
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]

    for y in range(int(y1), int(y2 + 1)):
        for x in range(int(x1), int(x2 + 1)):
            put_pixel(x, y)

def draw_filled_ellipse(vertices, filled=True):
    cx, cy = vertices[0]
    x_radius = abs(vertices[1][0] - cx)
    y_radius = abs(vertices[1][1] - cy)

    if filled:
        for y in range(int(cy - y_radius), int(cy + y_radius)):
            temp = (1 - ((y - cy) / y_radius)**2)
            if temp < 0:
                temp = 0
            x_start = cx - math.sqrt(x_radius**2 * temp)
            x_end = cx + math.sqrt(x_radius**2 * temp)

            for x in range(int(x_start), int(x_end) + 1):
                put_pixel(x, y)
def draw_empty_ellipse(vertices):
    cx, cy = vertices[0]
    x_radius = abs(vertices[1][0] - cx)
    y_radius = abs(vertices[1][1] - cy)

    for i in range(360):
        angle = math.radians(i)
        x = cx + x_radius * math.cos(angle)
        y = cy + y_radius * math.sin(angle)
        put_pixel(round(x), round(y))

def draw_filled_polygon(vertices):
    edges = [(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]

    min_y = min(vertex[1] for vertex in vertices)
    max_y = max(vertex[1] for vertex in vertices)

    for y in range(int(min_y), int(max_y + 1)):
        intersections = []

        for edge in edges:
            start_vertex, end_vertex = edge
            x1, y1 = start_vertex
            x2, y2 = end_vertex

            if min(y1, y2) <= y <= max(y1, y2):
                x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                intersections.append(x)
        intersections.sort()
        for i in range(0, len(intersections), 2):
            x_start, x_end = intersections[i], intersections[i + 1]
            for x in range(int(x_start), int(x_end) + 1):
                put_pixel(x, y)

def draw_empty_polygon(vertices, filled=True):
    edges = [(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]

    for edge in edges:
        start_vertex, end_vertex = edge
        x1, y1 = start_vertex
        x2, y2 = end_vertex

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        if dx > dy:
            steps = int(dx)
        else:
            steps = int(dy)

        x_increment = (x2 - x1) / steps
        y_increment = (y2 - y1) / steps

        x, y = x1, y1

        for _ in range(steps):
            x += x_increment
            y += y_increment
            put_pixel(round(x), round(y))

def draw_filled_square(vertices, filled=True):
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]
    size = min(abs(x2 - x1), abs(y2 - y1))

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    half_size = size / 2

    if filled:
        pass
    else:
        edges = [
            ((cx - half_size, cy - half_size), (cx + half_size, cy - half_size)),
            ((cx + half_size, cy - half_size), (cx + half_size, cy + half_size)),
            ((cx + half_size, cy + half_size), (cx - half_size, cy + half_size)),
            ((cx - half_size, cy + half_size), (cx - half_size, cy - half_size)),
        ]

        for edge in edges:
            start_vertex, end_vertex = edge
            x1, y1 = start_vertex
            x2, y2 = end_vertex

            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            if dx > dy:
                steps = int(dx)
            else:
                steps = int(dy)

            x_increment = (x2 - x1) / steps
            y_increment = (y2 - y1) / steps

            x, y = x1, y1

            for _ in range(steps):
                x += x_increment
                y += y_increment
                put_pixel(round(x), round(y))

def draw_star(vertices):
    x, y = vertices[0]
    size = abs(vertices[1][0] - x)

    inner_radius = size / 4
    outer_radius = size

    points = []
    for i in range(10):
        angle = math.radians(i * 72)
        outer_x = x + outer_radius * math.cos(angle)
        outer_y = y + outer_radius * math.sin(angle)
        points.append((outer_x, outer_y))

        angle += math.radians(36)
        inner_x = x + inner_radius * math.cos(angle)
        inner_y = y + inner_radius * math.sin(angle)
        points.append((inner_x, inner_y))
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)

    for y in range(int(min_y), int(max_y) + 1):
        intersections = []
        for i in range(len(points)):
            start_point = points[i]
            end_point = points[(i + 1) % len(points)]

            if min(start_point[1], end_point[1]) <= y <= max(start_point[1], end_point[1]):
                x = start_point[0] + (end_point[0] - start_point[0]) * (y - start_point[1]) / (end_point[1] - start_point[1])
                intersections.append(x)
        intersections.sort()
        for i in range(0, len(intersections), 2):
            x_start, x_end = intersections[i], intersections[i + 1]
            for x in range(int(x_start), int(x_end) + 1):
                put_pixel(x, y)

def draw_filled_star(vertices):
    x, y = vertices[0]
    size = abs(vertices[1][0] - x)

    inner_radius = size / 4
    outer_radius = size

    points = []
    for i in range(10):
        angle = math.radians(i * 36)
        if i % 2 == 0:
            radius = outer_radius
        else:
            radius = inner_radius
        point_x = x + radius * math.cos(angle)
        point_y = y + radius * math.sin(angle)
        points.append((point_x, point_y))
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    for y in range(int(min_y), int(max_y) + 1):
        intersections = []

        for i in range(len(points)):
            start_point = points[i]
            end_point = points[(i + 1) % len(points)]

            if min(start_point[1], end_point[1]) <= y <= max(start_point[1], end_point[1]):
                x = start_point[0] + (end_point[0] - start_point[0]) * (y - start_point[1]) / (end_point[1] - start_point[1])
                intersections.append(x)
        intersections.sort()
        for i in range(0, len(intersections), 2):
            x_start, x_end = intersections[i], intersections[i + 1]
            for x in range(int(x_start), int(x_end) + 1):
                put_pixel(x, y)

shapes = [
    Ston([(60, 260), (110, 310)], draw_filled_star, color=(0.2, 0.0, 0.7)),
    Ston([(160, 360), (210, 410)], draw_star, color=(0.5, 0.1, 0.8)),
    Ston([(210, 310), (310, 410), (410, 310)], draw_filled_polygon, color=(0.7, 0.2, 0.3)),
    Ston([(110, 460), (160, 410), (210, 460)], draw_empty_polygon, color=(0.8, 0.7, 0.9)),
    Ston([(110, 410), (410, 110)], draw_line, color=(0.2, 0.4, 0.3)),
    Ston([(60, 310), (160, 310)], draw_line, color=(0.7, 0.2, 0.49)),
    Ston([(210, 260), (260, 410), (310, 260)], draw_filled_triangle, color=(0.2, 0.4, 0.5)),
    Ston([(210, 110), (260, 260), (310, 110)], draw_empty_triangle, color=(0.8, 0.3, 0.9)),
    Ston([(410, 210), (440, 240)], draw_empty_circle, color=(0.2, 0.3, 0.3)),
    Ston([(410, 210), (440, 240)], draw_filled_circle, color=(0.2, 0.3, 0.3)),
    Ston([(310, 110), (360, 160)], draw_filled_disk, color=(0.1, 1.0, 1.0)),
    Ston([(110, 360), (160, 410)], draw_filled_square, color=(0.8, 0.2, 0.4)),
    Ston([(260, 260), (360, 260)], draw_smooth_curve, color=(0.3, 0.3, 0.7)),
    Ston([(210, 210), (260, 310)], draw_empty_rectangle, color=(0.4, 0.1, 0.0)),
    Ston([(210, 210), (310, 310)], draw_filled_rectangle, color=(0.4, 0.1, 0.0)),
    Ston([(310, 410), (340, 430)], draw_filled_ellipse, color=(0.5, 0.4, 0.1)),
    Ston([(110, 410), (140, 430)], draw_empty_ellipse, color=(0.9, 0.7, 0.3)),
]
def randomize_shapes():
    for shape in shapes:
        x_offset = random.uniform(-50, 50)
        y_offset = random.uniform(-50, 50)
        shape.translate((x_offset, y_offset))
        scale_factor = random.uniform(0.5, 1.5)
        center_x = sum(x for x, _ in shape.vertices) / len(shape.vertices)
        center_y = sum(y for _, y in shape.vertices) / len(shape.vertices)
        translation_vector = (-center_x, -center_y)
        shape.translate(translation_vector)
        shape.vertices = [(x * scale_factor, y * scale_factor) for x, y in shape.vertices]
        shape.translate((-translation_vector[0], -translation_vector[1]))


def initialize():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)


def translate_current_shape(translation_vector):
    global current_shape_index
    if 0 <= current_shape_index < len(shapes):
        shapes[current_shape_index].translate(translation_vector)
        glutPostRedisplay()


def switch_to_next_shape():
    global current_shape_index
    current_shape_index = (current_shape_index + 1) % len(shapes)
    glutPostRedisplay()

def draw_info():
    glColor3f(1.0, 1.0, 1.0)
    text = "KLAVYE KISAYOLLARI:\n"\
           "Z/C: Yakınlaştırma/Uzaklaştırma\n"\
           "C: Bir sonraki şekle geç\n"\
           "V: Şekli saat yönünde döndür\n"\
           "B: Şekli büyüt\n"\
           "N: Şekli küçült\n"\
           "M: Yatay olarak aynala (yansıt)\n"\
           "K: Kirpma işlevini aç/kapat\n"\
           "ESC: Çıkış"

    text_lines = text.split('\n')
    text_width = max(len(line) for line in text_lines) * 8
    text_height = 13 * len(text_lines)
    x_pos = 10
    y_pos = 10
    for line in reversed(text_lines):
        glRasterPos2i(x_pos, y_pos)
        for char in line:
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(char))
        y_pos += 13
def ekran():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, width, 0.0, height)
    apply_clipping()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(center[0], center[1], 0.0)
    glScalef(zoom_factor, zoom_factor, 1.0)
    glTranslatef(-center[0], -center[1], 0.0)

    for i, shape in enumerate(shapes):
        shape.draw(i == current_shape_index)

    draw_info()

    glutSwapBuffers()
    glDisable(GL_SCISSOR_TEST)

def zoom_in():
    global zoom_factor
    zoom_factor += 0.1
    if zoom_factor > 5.0:
        zoom_factor = 5.0
    glutPostRedisplay()


def zoom_out():
    global zoom_factor
    zoom_factor -= 0.1
    if zoom_factor < 0.1:
        zoom_factor = 0.1
    glutPostRedisplay()

def scale_current_shape(scale_factor):
    global current_shape_index
    if 0 <= current_shape_index < len(shapes):
        shape = shapes[current_shape_index]
        center_x = sum(x for x, _ in shape.vertices) / len(shape.vertices)
        center_y = sum(y for _, y in shape.vertices) / len(shape.vertices)
        translation_vector = (-center_x, -center_y)
        shape.translate(translation_vector)
        shape.vertices = [(x * scale_factor, y * scale_factor) for x, y in shape.vertices]
        shape.translate((-translation_vector[0], -translation_vector[1]))
        glutPostRedisplay()

def draw_horizontal_mirror(vertices, filled=True):
    glBegin(GL_POLYGON if filled else GL_LINE_LOOP)
    for vertex in vertices:
        glVertex2f(vertex[0], -vertex[1])
    glEnd()

def mirror_current_shape():
    global current_shape_index
    if 0 <= current_shape_index < len(shapes):
        shape_to_mirror = shapes[current_shape_index]
        mirrored_vertices = [(x, -y) for x, y in shape_to_mirror.vertices]
        mirror_shape = Shape(mirrored_vertices, shape_to_mirror.draw_function, shape_to_mirror.color)
        mirror_shape.angle = shape_to_mirror.angle
        shapes.append(mirror_shape)
        glutPostRedisplay()


def apply_clipping():
    if clipping_rectangle is not None and clipping_active:
        glEnable(GL_SCISSOR_TEST)
        glScissor(*clipping_rectangle)
    else:
        glDisable(GL_SCISSOR_TEST)

def mouse(button, state, x, y):
    global clipping_rectangle, clipping_active

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN and clipping_active:
            clipping_rectangle[2] = x
            clipping_rectangle[3] = height - y
            clipping_active = False
            toggle_clipping()
        elif state == GLUT_DOWN and not clipping_active:
            clipping_rectangle = [x, height - y, x, height - y]
            clipping_active = True
        elif state == GLUT_UP:
            clipping_rectangle[2] = x
            clipping_rectangle[3] = height - y
            clipping_active = False

    glutPostRedisplay()

def mouse_motion(x, y):
  if clipping_active:
    clipping_rectangle[2] = x
    clipping_rectangle[3] = height - y
    glutPostRedisplay()

def toggle_clipping():
    global clipping_active
    clipping_active = not clipping_active
    glutPostRedisplay()

def keyboard(key, x, y):
    global current_shape_index
    if key == b'z':
        zoom_in()
    elif key == b'x':
        zoom_out()
    elif key == b'c':
        switch_to_next_shape()
    elif key == b'v':
        rotate_current_shape()
    elif key == b'b':
        scale_current_shape(1.1)
    elif key == b'n':
        scale_current_shape(0.9)
    elif key == b'm':
        mirror_current_shape()
    elif key == b'k':
        toggle_clipping()
    elif key == b'\x1b':
        sys.exit()

    glutPostRedisplay()

def rotate_current_shape(angle_increment=10.0):
    global current_shape_index
    if 0 <= current_shape_index < len(shapes):
        shapes[current_shape_index].rotate(angle_increment)
        glutPostRedisplay()

def special_keys(key, x, y):
    if key == GLUT_KEY_LEFT or key == ord('a'):
        translate_current_shape((-translation_step, 0))
    elif key == GLUT_KEY_RIGHT or key == ord('d'):
        translate_current_shape((translation_step, 0))
    elif key == GLUT_KEY_UP or key == ord('w'):
        translate_current_shape((0, translation_step))
    elif key == GLUT_KEY_DOWN or key == ord('s'):
        translate_current_shape((0, -translation_step))

randomize_shapes()
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"211220073 Yunus Emre TAHA")

    initialize()
    glutDisplayFunc(ekran)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_motion)
    glutMainLoop()

if __name__ == "__main__":
    main()