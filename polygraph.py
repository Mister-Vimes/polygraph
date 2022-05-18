#!/usr/bin/env python3

# POLYGRAPH - A multi-layered pie chart data visualization

__author__      =   'Will Neely'
__copyright__   =   'Copyright 2022, Will Neely'

from tkinter import *
from tkinter import ttk
from PIL import Image
import math

# --- CLASSES ---

class Widget:   # generic widget (parent class)

    def __init__(self, root):
        self.frame = ttk.Frame(root, padding="4 4 4 4")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

    def destroy(self):
        self.frame.destroy()

class CatsWidget(Widget):   # categories widget

    def __init__(self, root, categories):
        Widget.__init__(self, root)
        valup = root.register(self.update)
        valid = root.register(self.validate)

        self.index = len(categories)
        self.name = StringVar()
        self.name.set('Category ' + str(len(categories) + 1))
        self.val = StringVar()
        # self.val.set('1')
        categories.append(self)
        
        self.frame.grid(column=0, row=self.index+1, sticky=(N, E, W))

        ttk.Label(self.frame, text='Category Label').grid(column=0, row=0, sticky=(W, N, E))
        cat_name = ttk.Entry(self.frame, width=10, textvariable=self.name, validate='key', validatecommand=(valup, '%P'))
        cat_name.grid(column=0, row=1, sticky=(N, E, W,))

        ttk.Label(self.frame, text='Size').grid(column=0, row=2, sticky=(W, N, E))
        cat_val = ttk.Entry(self.frame, width=10, textvariable=self.val, validate='key', validatecommand=(valid, '%P'))
        cat_val.grid(column=0, row=3, sticky=(N, E, W))

    def update(self, P):
        redraw_fields(categories, layers, nodes)
        rename_nodes(self.index, -1, P)
        params.to_top()
        return True

    def validate(self, P):
        # draw_pie()
        return True

class LayersWidget(Widget):   # layers widget

    def __init__(self, root, layers):
        Widget.__init__(self, root)
        valup = root.register(self.update)
        colorup = root.register(self.color_set)

        self.index = len(layers)
        self.name = StringVar()
        self.color_index = int(0)
        self.name.set('Layer ' + str(len(layers) + 1))
        layers.append(self)
        
        self.frame.grid(column=self.index+1, row=0, sticky='N E S W')

        ttk.Label(self.frame, text='Layer Label').grid(column=0, row=0, columnspan=2, sticky=(W, N))
        layer_name = ttk.Entry(self.frame, width=20, textvariable=self.name, validate='key', validatecommand=(valup, '%P'))
        layer_name.grid(column=0, row=1, columnspan=2, sticky=(W, N))


        self.square = Canvas(self.frame, height=20, width=30, background='#ccc')
        self.square.grid(column=1, row=2, sticky='W')
        ttk.Button(self.frame, text='Color', command=(colorup, -1)).grid(column=0, row=2, sticky=(W))
        self.color_set(0)
        redraw_fields(categories, layers, nodes)

    def color_set(self, i):
        clear = False
        i = int(i) if int(i) >= 0 else self.color_index
        while not clear:
            clear = True
            for j in range(len(layers)):
                if layers[j].color_index == i:
                    clear = False  
                    i = (i + 1) % len(color_options)
        self.color_index = int(i)
        self.color = color_options[self.color_index]
        bg_color = '#' + ''.join(list(map(lambda h: str(hex(int(h)))[2], self.color)))
        self.square.config(bg=bg_color)

    def update(self, P):
        redraw_fields(categories, layers, nodes)
        rename_nodes(-1, self.index, P)
        params.to_top()
        return True

class Node(Widget):   # node widget

    def __init__(self, root, categories, layers, cat, layer):
        Widget.__init__(self, root)
        valid = root.register(self.validate)

        self.cat = cat
        self.layer = layer
        self.name = StringVar()
        self.name.set('%s for %s' % (layers[layer].name.get(), categories[cat].name.get()))
        self.val = StringVar()
        # self.val.set('1')

        self.frame.grid(column=self.layer+1, row=self.cat+1, sticky=(W, N, E, S))

        ttk.Label(self.frame, textvariable=self.name, wraplength=220).grid(column=0, row=0, sticky=(W, N))
        node_val = ttk.Entry(self.frame, width=25, textvariable=self.val, validate='key', validatecommand=(valid, '%P'))
        node_val.grid(column=0, row=1, sticky=(W, N))

    def update(self, categories, layers):
        self.name.set(layers[self.layer].name.get() + ' for ' + categories[self.cat].name.get())

    def validate(self, P):
        return True

class ParamsWidget(Widget):   # parameters widget

    def __init__(self, root, layers):
        Widget.__init__(self, root)

        self.name = 'Parameter Controls'
        self.title = StringVar()
        self.upper_bound = StringVar()
        
        self.frame.grid(column=0, row=0, sticky=(N, E, S, W))

        ttk.Label(self.frame, text='Graph Title: ').grid(column=0, row=1, sticky=(E))
        graph_title = ttk.Entry(self.frame, width=20, textvariable=self.title)
        graph_title.grid(column=1, row=1, sticky=(N, E, W))

        ttk.Button(self.frame, text='Add Layer', command=self.add_layer, state='!disabled').grid(column=1, row=2, sticky=(N, E, W))
        ttk.Button(self.frame, text='Remove Layer', command=self.remove_layer, state='!disabled').grid(column=1, row=3, sticky=(E, S, W))        
        ttk.Button(self.frame, text='Add Category', command=self.add_cat, state='!disabled').grid(column=0, row=2, sticky=(N, E, W))
        ttk.Button(self.frame, text='Remove Category', command=self.remove_cat, state='!disabled').grid(column=0, row=3, sticky=(E, S, W))

        ttk.Label(self.frame, text='Maximum Layer Value\n(optional)').grid(column=0, row=4, sticky=(E))
        upper_bound = ttk.Entry(self.frame, width=10, textvariable=self.upper_bound)
        upper_bound.grid(column=1, row=4, sticky=(N, E, W))

    def add_layer(self):
        if len(layers) < 4:
            LayersWidget(mainframe, layers)

    def remove_layer(self):
        if len(layers) > 1:
            layers[-1].destroy()
            layers.pop(-1)
            redraw_fields(categories, layers, nodes)        

    def add_cat(self):
        if len(categories) < 6:
            CatsWidget(mainframe, categories)
            redraw_fields(categories, layers, nodes)

    def remove_cat(self):
        if len(categories) > 1:
            categories[-1].destroy()
            categories.pop(-1)
            redraw_fields(categories, layers, nodes)    

    def to_top(self):
        self.frame.lift(self.frame)
  
# --- FUNCTIONS ---

# generic math helps

def avg(a, b):
    return (a + b) / 2

def sum_down(a):
    return 1 if a == 1 else a + sum_down(a - 1)

def combinations(a):
    result = 1
    if a > 1:
        result += a 
    if a > 2:
        result += a 
    if a > 3:
        result += (a - 3) * sum_down(a - 1) * sum_down(a - 3)

# QoL feature: Redraw / relabel node fields per [layer][category] on every change

def node_fit(a, b, layer):
    while len(a) > len(b):
        if layer < 0:
            for n in a[-1]:    # destroy a's children
                n.destroy()
        else: 
            a[-1].destroy()
        a.pop(-1)

    while len(a) < len(b):
        if layer < 0:    # not specific to a layer (a is itself a layer)
            a.append([])
        else:
            a.append(Node(mainframe, categories, layers, len(a), layer))            

def redraw_fields(categories, layers, nodes):
    node_fit(nodes, layers, -1)

    for i in range(len(nodes)):
        node_fit(nodes[i], categories, i)

def rename_nodes(cat, layer, val):
    for i in range(len(nodes)):
        if layer >= 0 and layer != i:
            continue
        for j in range(len(nodes[i])):
            if cat >= 0 and cat != j:
                continue
            cat_name = val if cat >= 0 else categories[j].name.get()
            layer_name = val if layer >= 0 else layers[i].name.get()

            nodes[i][j].name.set('%s for %s' % (layer_name, cat_name))

def total_cat():    # get cats total
    cats_total = 0
    for c in categories:
        cats_total += int(c.val.get()) if c.val.get().isnumeric() else 0.001
    return cats_total

def alter(a, d):    # convert a, d to x, y
    return int(math.cos(a * math.pi / 180) * d + pie_center), int(math.sin(a * math.pi / 180) * d + pie_center)

def find_intersect(a, b, j, k):  # a[j][k][1] is less than or equals b[j][k][1]
    while a[j][k][1] <= b[j][k][1]:
        j += (k + 1) // smooth 
        k = k + 1 % smooth
    return j, k

def stringify_color(blend, i):
    return '#' + ''.join(list(map(lambda h: str(hex(int(h)))[2], blend[i])))

def color_mixer(a, b, n):    # new color a, old mix b
    result = []
    for c in range(3):
        result.append(int(avg(a[c] / n, b[c] * (n - 1) / n)) * 2)
    return result

# generate polygon points
# [layer], [cat], [[a, d], [a, d]...]

def find_polygon(points, i, j, key):
    new_polygon = []
    for k in range(smooth):
        n = min(map(lambda x: points[x][j][k][1], key))
        new_polygon.append([points[0][j][k][0], n])
    return new_polygon

def draw_points():
    for s in shapes:
        pie.delete(s)

    points = []

    # find scale, position, and ceiling

    pos = []
    cats_total = total_cat()
    ceiling = 0    
    cat_sizes = []
    position = 0

    for i in range(len(categories)):

        pos.append(position)
        cat_sizes.append(int(categories[i].val.get()) if categories[i].val.get().isnumeric() and int(categories[i].val.get()) > 0 else 0.001)
        position += cat_sizes[-1]

        for j in range(len(layers)):
            v = math.sqrt(int(nodes[j][i].val.get())) if nodes[j][i].val.get().isnumeric() and int(nodes[j][i].val.get()) > 0 else 0.001
            ceiling = max(ceiling, v)
            try:
                floor = min(v, floor)
            except UnboundLocalError:
                floor = math.sqrt(v)
        smallest_diff = min(cat_sizes)

    if params.upper_bound.get().isnumeric():
        ceiling = max(math.sqrt(float(params.upper_bound.get())), .01)
        ceiling += (ceiling - floor) / (smooth - 2)
    else:
        ceiling += ceiling * 0.1     # implement scale variable here

    # determine points [layers][cats][a, d]

    for i in range(len(layers)):
        points.append([])
 
        for j in range(len(categories)):
            points[i].append([])
            if j + 1 >= len(pos):
                diff = (cats_total - pos[j])
            else:
                diff = (pos[j + 1] - pos[j])
            val = (int(nodes[i][j].val.get()) if nodes[i][j].val.get().isnumeric() and int(nodes[i][j].val.get()) > 0 else 0.001) * smallest_diff / diff
            val = max(floor, min(ceiling, math.sqrt(val)))    # complicated enough for 2 lines
            diff /= (smooth - 1)
            for k in range(smooth):        
                points[i][j].append([(pos[j] + diff * k) / cats_total * 360 % 360, val / ceiling * pie_rad])

    different_vals = False   # check if smoothing is necessary

    for p in points:
        for i in range(len(p)):
            if p[i][0][1] != p[i -1][0][1]:
                different_vals = True

    # smooth lines

    if different_vals:
        for p in points:
            full_right = p[0][0][1]
            for j in range(len(categories)):
                left, right = p[j][0][1], p[j][-1][1]
                left_shift = (avg(p[j - 1][-1][1], left) if j == 0 else p[j - 1][-1][1]) - left
                right_shift = avg(right, (full_right if j + 1 >= len(categories) else p[j + 1][0][1])) - right

                all_shift = -(left_shift + right_shift) / (smooth - 2)
                c = int(abs(left_shift) / (abs(left_shift) + abs(right_shift)) * smooth)

                p[j][0][1] = left + left_shift
                p[j][-1][1] = right + right_shift

                k, left_push, right_push = 1, 0, 0
                while (k <= c or smooth - k > c) and k < smooth:
                    if k <= c and left_shift != 0:
                        shift = left_push + all_shift + .618 * (p[j][k - 1][1] - p[j][k][1] + all_shift)
                        p[j][k][1] += shift
                        left_push -= (.618 * (p[j][k - 1][1] - p[j][k][1])) / (c - k if c != k else 1)
                    if smooth - k > c and right_shift != 0:
                        shift = right_push + all_shift + .618 * (p[j][smooth - k][1] - p[j][smooth - k - 1][1] + all_shift)
                        p[j][smooth - k - 1][1] += shift
                        right_push -= (.618 * (p[j][k - 1][1] - p[j][k][1])) / (smooth - k - c)
                
                    k += 1

    # combine / split polygons via layer comparison; mix colors based on transparency

    b1, b2, b3, b4 = [], [], [], []
    k1, k2, k3, k4 = [], [], [], []

    for i in range(len(layers)):
        b1.append(layers[i].color)
        k1.append([i])
        for j in range(i + 1, len(layers)):
            b2.append(color_mixer(layers[i].color, layers[j].color, 2))
            k2.append([i, j])
            for k in range(j + 1, len(layers)):
                b3.append(color_mixer(layers[k].color, color_mixer(layers[j].color, layers[i].color, 2), 3))
                k3.append([i, j, k])
                for l in range(k + 1, len(layers)):
                    b4.append(color_mixer((color_mixer(layers[i].color, layers[j].color, 2)), (color_mixer(layers[k].color, layers[l].color, 2)), 2))
                    k4.append([i, j, k, l])

    blend = b1 + b2 + b3 + b4
    key = k1 + k2 + k3 + k4
    for i in range(len(layers), len(blend)):
        points.append([])
        for j in range(len(categories)):
            points[i].append(find_polygon(points, i, j, key[i]))
    
    draw_polygons(points, blend)
    draw_key(blend)

def draw_polygons(points, blend):    # draw polygons
    for i in range(len(points)):
        for q in points[i]:
            plots = [pie_center, pie_center]
            for r in q:
                xx, yy = alter(r[0], r[1])
                plots += [xx, yy]

            color = stringify_color(blend, i)
            shapes.append(pie.create_polygon(*plots, fill=color))

# draw pie, add labels

def sort_label(labels, b, c, label):
    clear = False
    while not clear:
        if len(labels[label]) > 1 or len(labels[label]) == 1 and label in [0, 1]:
            label += 1
        else:
            labels[label].append([b, c.name.get()])
            clear = True

def draw_pie():
    shapes.append(pie.create_oval(pie_nw, pie_nw, pie_se, pie_se, outline='black', fill=''))

    labels = [[], [], [], []]
    cats_total = total_cat()
    cats_track = 0
    if len(categories) > 1:
        for c in categories:
            cat_val = int(c.val.get()) if c.val.get().isnumeric() and int(c.val.get()) > 0 else 0.001
            a = (cats_track / cats_total * 360) % 360
            x, y = alter(a, pie_rad)
            shapes.append(pie.create_line(pie_center, pie_center, x, y, fill='black'))
            cats_track += cat_val
            b = avg(a, (cats_track / cats_total * 360)) % 360
            label = int(b / 90)
            sort_label(labels, b, c, label)

    for i in range(len(labels)):
        for j in range(len(labels[i])):
            angle = labels[i][j][0]
            a, b = alter(angle, pie_rad)
            x, y = alter(angle, int(pie_rad * 1.01))
            dir = 1 if i in [0, 3] else -1
            y_adjust = .2 * ((270 - angle) % 180)
            y += y_adjust * (1 if i in [0, 1] else -1)
            x += dir * (60 - y_adjust)
            vert = 'n' if i < 2 else 's'
            hor = 'e' if i in range(1, 3) else 'w'
            shapes.append(pie.create_line(a, b, x, y, fill='black'))
            shapes.append(pie.create_text(x, y, text=labels[i][j][1], width=pie_nw - (60 - y_adjust), anchor=vert + hor, font=('TkMenuFont', 14), fill='black'))

    if params.title.get():
        shapes.append(pie.create_text(100, 25, text=params.title.get(), width=canvas_width - 200, anchor='nw', font=('TkHeadingFont', 38), fill='black', justify='center'))
    
    if not hide_credit:
        shapes.append(pie.create_text(30, canvas_height - 30, text='Created using Polygraph: www.willneelycoding.wordpress.com', anchor='nw', fill='black'))

def draw_key(blend):
    for i in range(len(layers)):
        shapes.append(pie.create_text(canvas_width - 110, 200 + (50 * i), anchor='nw', width=100, text=layers[i].name.get(), font=('TkMenuFont', 14), fill='black'))
        shapes.append(pie.create_rectangle(canvas_width - 150, 201 + (50 * i), canvas_width - 120, 216 + (50 * i), fill=stringify_color(blend, i), outline='black'))

# Update function

def update_all():
    redraw_fields(categories, layers, nodes)
    draw_points()
    draw_pie()
    params.to_top()

# Export graphic

def export_graph():
    pie.postscript(file='pie.eps')
    graph = Image.open('pie.eps')
    graph.save(f'polygraph.png', 'png')    

# Main Program

# Init variables and parameters

shapes, categories, layers, nodes, points = [], [], [], [], []
title = 'Polygraph'
canvas_width = 1080
canvas_height = 800
max_cats = 6
max_layers = 4
pie_nw = 200
pie_se = 750
smooth = 70      # Higher number = smoother curves and better joins
hide_credit = False
color_options = [
    [3, 1, 11],
    [15, 0, 0],
    [0, 0, 15],
    [0, 15, 0],
    [0, 7, 9],
    [7, 9, 0],
    [9, 0, 7],
    [11, 3, 1],
    [1, 11, 3],
]

scale = 1    # for later use

# Computed variables

pie_center = (pie_se - pie_nw) // 2 + pie_nw
pie_rad = float((pie_se - pie_nw) / 2)

# Root window and main frame

root = Tk()
root.title(title)

mainframe = ttk.Frame(root, padding='2 2 2 2', height=800, width=1020)
mainframe.grid(column=0, row=0, sticky=(N, E, S, W))
mainframe.update = mainframe.register(update_all)
mainframe.export = mainframe.register(export_graph)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

pie = Canvas(mainframe, width=canvas_width, height=canvas_height, background='white')
pie.grid(column=max_layers+1, row=0, rowspan=max_cats+2, sticky=(N, E, S, W))
params = ParamsWidget(mainframe, layers)
draw_pie()

ttk.Button(mainframe, text="Update\ngraph", command=mainframe.update, state='!disabled', padding='2 2 8 8').grid(column=1, row=7, sticky=(W, N, S))
ttk.Button(mainframe, text="Export\nto file", command=mainframe.export, state='!disabled', padding='2 2 8 8').grid(column=0, row=7, sticky=(W, N, S))

# Vars - Categories

for _ in range(3):
    CatsWidget(mainframe, categories)

LayersWidget(mainframe, layers)

# Vars panel

# Vars - Layers

# Draw canvas and pie

# Begin loop

root.mainloop()