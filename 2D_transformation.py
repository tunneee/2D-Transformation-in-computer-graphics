import tkinter as tk
from tkinter import ttk
import numpy as np
import itertools
import math
import cv2
np.set_printoptions(suppress=True)
window = tk.Tk()
window.title("2D Transformations")

window.tk.call("source", "azure.tcl")
window.tk.call("set_theme", "dark")

canvas = tk.Canvas(width=800, height=800, bg="grey")
canvas.grid(row=0, column=0, rowspan=15, columnspan=15)

global vertices
vertices = [
    [0, 0],
    [100, 0],
    [100, 100],
    [0, 100]
]
rectangle = canvas.create_polygon(vertices, fill='black')


def on_mouse_press(event):
    x = event.x
    y = event.y

    global start_x, start_y
    start_x = x
    start_y = y
    # print(start_x, start_y)


def flatten(list_of_lists):
    """Flatten one level of nesting"""
    return itertools.chain.from_iterable(list_of_lists)


def on_mouse_release(event):
    x = event.x
    y = event.y
    global end_x, end_y
    end_x = x
    end_y = y
    # print(end_x, end_y)
    width = end_x - start_x
    height = end_y - start_y
    global vertices
    vertices = [
        [start_x, start_y],
        [start_x + width, start_y],
        [start_x + width, start_y + height],
        [start_x, start_y + height]
    ]
    canvas.coords(rectangle, *flatten(vertices))

    canvas.unbind("<Motion>")


canvas.bind("<Button-1>", on_mouse_press)
canvas.bind("<ButtonRelease-1>", on_mouse_release)

transform_frame = tk.Frame(window)
transform_frame.grid(row=0, column=15)


def apply_transform():
    x_transform = x_transform_input.get()
    y_transform = y_transform_input.get()
    global vertices
    translate_matrix = np.array([[1, 0, float(x_transform)],
                                 [0, 1, float(y_transform)],
                                 [0, 0, 1]])
    for i in range(len(vertices)):
        vertices[i] = np.array([[vertices[i][0]], [vertices[i][1]], [1]])
        vertices[i] = np.matmul(translate_matrix, vertices[i])
        vertices[i] = [int(vertices[i][0][0]), int(vertices[i][1][0])]
    canvas.coords(rectangle, *flatten(vertices))

    canvas.unbind("<Motion>")


def apply_scale():
    scale = scale_input.get()

    global vertices
    scaling_matrix = np.array([[float(scale), 0, 0],
                               [0, float(scale), 0],
                               [0, 0, 1]])
    old_center = [(vertices[0][0] + vertices[2][0]) / 2,
                  (vertices[0][1] + vertices[2][1]) / 2]
    for i in range(len(vertices)):
        vertices[i] = np.array([[vertices[i][0]], [vertices[i][1]], [1]])
        vertices[i] = np.matmul(scaling_matrix, vertices[i])
        vertices[i] = [int(vertices[i][0][0]), int(vertices[i][1][0])]
    new_center = [(vertices[0][0] + vertices[2][0]) / 2,
                  (vertices[0][1] + vertices[2][1]) / 2]
    x_transform = old_center[0] - new_center[0]
    y_transform = old_center[1] - new_center[1]
    translate_matrix = np.array([[1, 0, float(x_transform)],
                                 [0, 1, float(y_transform)],
                                 [0, 0, 1]])
    for i in range(len(vertices)):
        vertices[i] = np.array([[vertices[i][0]], [vertices[i][1]], [1]])
        vertices[i] = np.matmul(translate_matrix, vertices[i])
        vertices[i] = [int(vertices[i][0][0]), int(vertices[i][1][0])]
    canvas.coords(rectangle, *flatten(vertices))
    canvas.unbind("<Motion>")


def rotate(points, angle, center):
    angle = math.radians(angle)
    cos_val = math.cos(angle)
    sin_val = math.sin(angle)
    cx, cy = center
    new_points = []
    for x_old, y_old in points:
        x_old -= cx
        y_old -= cy
        x_new = x_old * cos_val - y_old * sin_val
        y_new = x_old * sin_val + y_old * cos_val
        new_points.append([x_new + cx, y_new + cy])
    return new_points


def apply_rotate():
    rotate_angle = float(rotate_input.get())
    global vertices
    center = [(vertices[0][0] + vertices[2][0]) / 2,
              (vertices[0][1] + vertices[2][1]) / 2]
    vertices = rotate(vertices, rotate_angle, center)
    canvas.coords(rectangle, *flatten(vertices))
    canvas.unbind("<Motion>")


def apply_perspective():
    transformed_vertices = [[point_1_x_input.get(), point_1_y_input.get()],
                            [point_2_x_input.get(), point_2_y_input.get()],
                            [point_3_x_input.get(), point_3_y_input.get()],
                            [point_4_x_input.get(), point_4_y_input.get()]]
    transformed_vertices = np.array(transformed_vertices, dtype=np.float32)
    global vertices
    vertices_cp = np.array(vertices, dtype=np.float32)
    perspective_rect = canvas.create_polygon(
        *flatten(transformed_vertices), fill="red")
    matrix = cv2.getPerspectiveTransform(vertices_cp, transformed_vertices)
    output_matrix_text.delete(1.0, tk.END)
    output_matrix_text.insert(tk.END, matrix)


def pick_points():
    canvas.unbind('<Button-1>')
    canvas.unbind("<ButtonRelease-1>")
    canvas.destroy()
    global count
    count = 0

    global pick_points_canvas
    pick_points_canvas = tk.Canvas(width=800, height=800, bg="black")
    pick_points_canvas.grid(row=0, column=0, rowspan=15, columnspan=15)

    def on_mouse_press_(event):
        x = event.x
        y = event.y
        # print(x, y)
        global count
        count += 1
        if count == 1:
            point_1_x_input.delete(0, tk.END)
            point_1_x_input.insert(0, x)
            point_1_y_input.delete(0, tk.END)
            point_1_y_input.insert(0, y)
            pick_points_canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
        elif count == 2:
            point_2_x_input.delete(0, tk.END)
            point_2_x_input.insert(0, x)
            point_2_y_input.delete(0, tk.END)
            point_2_y_input.insert(0, y)
            pick_points_canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
        elif count == 3:
            point_3_x_input.delete(0, tk.END)
            point_3_x_input.insert(0, x)
            point_3_y_input.delete(0, tk.END)
            point_3_y_input.insert(0, y)
            pick_points_canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
        elif count == 4:
            point_4_x_input.delete(0, tk.END)
            point_4_x_input.insert(0, x)
            point_4_y_input.delete(0, tk.END)
            point_4_y_input.insert(0, y)
            pick_points_canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
            pick_points_canvas.create_polygon([[point_1_x_input.get(), point_1_y_input.get()],
                                               [point_2_x_input.get(),
                                                point_2_y_input.get()],
                                               [point_3_x_input.get(),
                                                point_3_y_input.get()],
                                               [point_4_x_input.get(), point_4_y_input.get()]], fill="black", outline="red")
            output_matrix_text.delete(1.0, tk.END)
            output_matrix_text.insert(
                tk.END, "Press anywhere on the canvas to return")
        # print(count)
        elif count == 5:
            return_normal_state()

    pick_points_canvas.bind("<Button-1>", on_mouse_press_)

    def return_normal_state():
        # pick_points_canvas.unbind('<Button-1>')
        # pick_points_canvas.destroy()
        # canvas.configure(state='normal')
        # # canvas.grid(row=0, column=0, rowspan=15, columnspan=15)
        output_matrix_text.delete(1.0, tk.END)
        global canvas
        canvas = tk.Canvas(width=800, height=800, bg="grey")
        canvas.grid(row=0, column=0, rowspan=15, columnspan=15)
        global rectangle
        rectangle = canvas.create_polygon(vertices, fill='black')
        canvas.bind("<Button-1>", on_mouse_press)
        canvas.bind("<ButtonRelease-1>", on_mouse_release)


def reset():
    global vertices
    vertices = vertices = [
        [0, 0],
        [100, 0],
        [100, 100],
        [0, 100]
    ]
    canvas.delete("all")
    output_matrix_text.delete(1.0, tk.END)
    x_transform_input.delete(0, tk.END)
    y_transform_input.delete(0, tk.END)

    scale_input.delete(0, tk.END)
    rotate_input.delete(0, tk.END)
    point_1_x_input.delete(0, tk.END)
    point_1_y_input.delete(0, tk.END)
    point_2_x_input.delete(0, tk.END)
    point_2_y_input.delete(0, tk.END)
    point_3_x_input.delete(0, tk.END)
    point_3_y_input.delete(0, tk.END)
    point_4_x_input.delete(0, tk.END)
    point_4_y_input.delete(0, tk.END)

    global rectangle
    rectangle = canvas.create_polygon(vertices, fill='black')
    canvas.bind("<Button-1>", on_mouse_press)
    canvas.bind("<ButtonRelease-1>", on_mouse_release)
    # canvas.unbind("<Motion>")


transform_label = tk.Label(transform_frame, text="Translation")
transform_label.grid(row=0, column=1, columnspan=3)

x_label = tk.Label(transform_frame, text="X")
x_label.grid(row=1, column=1)

x_transform_input = tk.Entry(transform_frame, text="X", width=10)
x_transform_input.grid(row=1, column=2, columnspan=2)

y_label = tk.Label(transform_frame, text="Y")
y_label.grid(row=2, column=1)
y_transform_input = tk.Entry(transform_frame, text="Y", width=10)
y_transform_input.grid(row=2, column=2, columnspan=2, padx=5, pady=5)

apply_transform_button = ttk.Button(
    transform_frame, text="Apply Translation", style='Accent.TButton', command=apply_transform)
apply_transform_button.grid(row=3, column=3, padx=5, pady=5)


scale_frame = tk.Frame(window)
scale_frame.grid(row=1, column=15)

scale_label = tk.Label(scale_frame, text="Scale")
scale_label.grid(row=4, column=1, columnspan=3)

scale_input = tk.Entry(scale_frame)
scale_input.grid(row=5, column=2, columnspan=2, padx=5, pady=5)

apply_scale_button = ttk.Button(
    scale_frame, text="Apply Scale", style='Accent.TButton', command=apply_scale)
apply_scale_button.grid(row=6, column=3, padx=5, pady=5)

rotate_frame = tk.Frame(window)
rotate_frame.grid(row=2, column=15)

rotate_label = tk.Label(rotate_frame, text="Rotate")
rotate_label.grid(row=7, column=1, columnspan=3)

rotate_input = tk.Entry(rotate_frame, text="Rotate", width=10)
rotate_input.grid(row=8, column=2, columnspan=2, padx=0, pady=5)

degrees_label = tk.Label(rotate_frame, text="Degrees")
degrees_label.grid(row=8, column=4)

apply_rotate_button = ttk.Button(
    rotate_frame, text="Apply Rotate", style='Accent.TButton', command=apply_rotate)
apply_rotate_button.grid(row=9, column=3, columnspan=2, padx=5, pady=5)

perspective_frame = tk.Frame(window)
perspective_frame.grid(row=3, column=15)

perspective_label = tk.Label(perspective_frame, text="Perspective Transformation")
perspective_label.grid(row=10, column=1, columnspan=3)

point_1_label = tk.Label(perspective_frame, text="Point 1")
point_1_label.grid(row=11, column=1)

point_1_x_input = tk.Entry(perspective_frame, width=5)
point_1_x_input.grid(row=11, column=2)

point_1_y_input = tk.Entry(perspective_frame, width=5)
point_1_y_input.grid(row=11, column=3)

point_2_label = tk.Label(perspective_frame, text="Point 2")
point_2_label.grid(row=12, column=1)

point_2_x_input = tk.Entry(perspective_frame, width=5)
point_2_x_input.grid(row=12, column=2)

point_2_y_input = tk.Entry(perspective_frame, width=5)
point_2_y_input.grid(row=12, column=3)

point_3_label = tk.Label(perspective_frame, text="Point 3")
point_3_label.grid(row=13, column=1)

point_3_x_input = tk.Entry(perspective_frame, width=5)
point_3_x_input.grid(row=13, column=2)

point_3_y_input = tk.Entry(perspective_frame, width=5)
point_3_y_input.grid(row=13, column=3)

point_4_label = tk.Label(perspective_frame, text="Point 4")
point_4_label.grid(row=14, column=1)

point_4_x_input = tk.Entry(perspective_frame, width=5)
point_4_x_input.grid(row=14, column=2)

point_4_y_input = tk.Entry(perspective_frame, width=5)
point_4_y_input.grid(row=14, column=3)

pick_points_button = ttk.Button(
    perspective_frame, text="Pick Points", style='Accent.TButton', command=pick_points)
pick_points_button.grid(row=15, column=1, padx=5, pady=5)

apply_perspective_button = ttk.Button(
    perspective_frame, text="Apply Perspective Transformation", style='Accent.TButton', command=apply_perspective)
apply_perspective_button.grid(row=15, column=3, padx=5, pady=5)

output_matrix_label = tk.Label(
    perspective_frame, text="Perspective Transformation Matrix")
output_matrix_label.grid(row=16, column=1, columnspan=3)

output_matrix_text = tk.Text(perspective_frame, height=5, width=50)
output_matrix_text.grid(row=17, column=1, columnspan=3, padx=5, pady=5)
output_matrix_text.insert(tk.END, "Matrix will be displayed here")

reset_button = ttk.Button(perspective_frame, text="Reset",
                          style='Accent.TButton', command=reset)
reset_button.grid(row=18, column=1, columnspan=3, padx=5, pady=5)

credit_label = tk.Label(window, text="Written by: Ho Huu Tuong aka Tunne ")
credit_label.grid(row=4, column=15, padx=5)

year_label = tk.Label(window, text="2023")
year_label.grid(row=5, column=15, padx=5)
window.mainloop()
