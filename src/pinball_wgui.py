import numpy as np
import math
import tkinter as tk

from numpy.lib.function_base import flip

import time


'''
    adjusted from: https://github.com/matthias-research/pages/blob/master/tenMinutePhysics/04-pinball.html
'''
    
cHeight = 900        
cWidth = int(3 / 5 * cHeight)

window = tk.Tk()
canvas = tk.Canvas(window, bg="white", width=cWidth, height=cHeight)
canvas.pack()

# utility functions
def vector_length(x):
    '''returns the length of a vector'''
    return np.sqrt(x.dot(x))    # faster than np.linalg.norm(x)


def closest_point_on_segment(p, a, b):
    ab = b - a
    t = ab.dot(ab)

    # a = b -> closest point is a resp. b
    if (t == 0.0):
        return np.copy(a)

    t = max(0.0, min(1.0, (p.dot(ab) - a.dot(ab)) / t))
    return a + ab * t


class Ball:
    def __init__(self, pos, vel, radius, mass, restitution):
        self.radius = radius
        self.mass = mass
        self.pos = pos
        self.vel = vel 
        self.restitution = restitution


    def simulate(self, dt, g):
        self.vel += g * dt
        self.pos += self.vel * dt

    

class Flipper:
    def __init__(self, pos, length, radius, rest_angle, max_rotation, angular_vel, window, button):
        self.pos = pos
        self.length = length
        self.radius = radius
        self.rest_angle = rest_angle
        self.max_rotation = abs(max_rotation)
        self.sign = math.copysign(1, max_rotation)
        self.angular_vel = angular_vel
        
        self.rotation = 0.0
        self.current_angular_vel = 0.0
        self.is_pressed = False

        window.bind(f'<KeyPress-{button}>', self.activate)
        window.bind(f'<KeyRelease-{button}>', self.deactivate)

    
    def simulate(self, dt):
        prev_rotation = self.rotation
        
        if (self.is_pressed):
            self.rotation = min(self.rotation + dt * self.angular_vel, self.max_rotation)
        else:
            self.rotation = max(self.rotation - dt * self.angular_vel, 0.0)
        
        self.current_angular_vel = self.sign * (self.rotation - prev_rotation) / dt

    def select(self, pos):
        dist = self.pos - pos
        return vector_length(dist) - vector_length(self.length)


    def activate(self, event):
        self.is_pressed = True

    
    def deactivate(self, event):
        self.is_pressed = False


    def rotate(self, angle):
        #Rotation: Translate Middle to the Origin, do simple rotation, translate back
        #Clockwise 45 degrees = r = np.array(((np.cos(theta),-np.sin(theta)),(np.sin(theta),np.cos(theta))))
        theta = np.radians(angle)
        trans_x = self.pos[5][0]
        trans_y = self.pos[5][1]

        c = np.copy(self.pos)
        # rotation
        for i in c:
            #NP Array of 2D Vect
            #Translate to Origin
            i[0] = i[0] - trans_x
            i[1] = i[1] - trans_y
            tmpx = i[0]
            tmpy = i[1]

            i[0] = np.cos(theta) * tmpx + (-np.sin(theta)) * tmpy
            i[1] = np.sin(theta) * tmpx + np.cos(theta) * tmpy
                
            i[0] = i[0] + trans_x
            i[1] = i[1] + trans_y
        return c



class CircleObstacle:
    def __init__(self, pos, radius, push_vel):
        self.pos = np.copy(pos)
        self.radius = radius
        self.push_vel = push_vel



class PhysicsScene:
    def __init__(self, border, balls, obstacles, flippers, g=np.array([0, 981]), dt=1/120):
        self.border = border
        self.balls = balls
        self.obstacles = obstacles
        self.flippers = flippers
        self.g = g
        self.dt = dt
        
        self.score = 0
        self.paused = True


def setup_scene() -> PhysicsScene:
    global window
    #scene borders --> Define set of pixel pairs
    border = np.array([[0.0, 0.0], [0.0,cHeight*0.7], [cWidth*0.3,cHeight*0.9], [cWidth*0.3,cHeight], [cWidth*0.7,cHeight], [cWidth*0.7,cHeight*0.9], [cWidth, cHeight*0.7], [cWidth, 0.0]])

    # balls
    radius = 10
    mass = math.pi * radius**2
    restitution = 1.0
    pos1 = np.array([cWidth * 0.25, cHeight * 0.05])
    vel1 = np.array([-1500.0, 0.0])
    ball1 = Ball(pos1, vel1, radius, mass,restitution)

    pos2 = np.array([cWidth * 0.8, cHeight * 0.6])
    vel2 = np.array([0.0, 0.0])
    ball2 = Ball(pos2, vel2, radius, mass,restitution)
    balls = [ball1, ball2]

    # obstacles
    obstacles = []
    obstacles.append(CircleObstacle(np.array([0.25 * cWidth, 0.2 * cHeight]), 70, 200.0))
    obstacles.append(CircleObstacle(np.array([0.75 * cWidth, 0.4 * cHeight]), 50, 200.0))
    obstacles.append(CircleObstacle(np.array([0.65 * cWidth, 0.7 * cHeight]), 40, 200.0))
    obstacles.append(CircleObstacle(np.array([0.2 * cWidth, 0.61 * cHeight]), 50, 200.0))

    # flippers
    radius = int(cWidth * 0.02)
    length = int(cWidth * 0.15)
    max_rotation = -80
    rest_angle = 30
    angular_vel = 1000
    restitution = 1.0
    x1 = cWidth * 0.3 
    y1 = cHeight * 0.9 
    x2 = cWidth * 0.7 
    y2 = cHeight * 0.9 
    flipper1 = Flipper(np.array([[x1,y1+radius+radius], [x1+length,y1+radius+radius], [x1+length,y1+radius], [x1+length,y1], [x1,y1], [x1,y1+radius]]), length, radius, rest_angle, max_rotation, angular_vel, window, 'a')
    flipper2 = Flipper(np.array([[x2,y2+radius+radius], [x2-length,y2+radius+radius], [x2-length,y2+radius], [x2-length,y2], [x2,y2], [x2,y2+radius]]), length, radius, -rest_angle, -max_rotation, angular_vel, window, 'd')
    flippers = [flipper1, flipper2]

    physics_scene = PhysicsScene(border, balls, obstacles, flippers)
    return physics_scene


def draw_disc(x, y, radius, col):
    canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=col, outline='')


def draw(physics_scene):
    global canvas
    # if we don't delete all canvas objects, tkinter will keep all objects in memory and always create new ones when drawing another object
    # this will create performance issues and potentially out of memory issue
    # TODO: maybe use "move" method for certain objects instead of redrawing (?)
    canvas.delete("all")
    
    #Draw Frame around GUI:
    canvas.create_polygon(physics_scene.border.flatten().tolist(),outline="black",fill="white")

    #Draw the balls:
    for b in physics_scene.balls:
        draw_disc(b.pos[0], b.pos[1], b.radius, "green")

    #Draw the obstacles:
    for o in physics_scene.obstacles:
        draw_disc(o.pos[0], o.pos[1], o.radius, "blue")
  
    #Draw the flippers
    for f in physics_scene.flippers:
        new_coords = f.rotate(f.rest_angle + f.rotation * f.sign)
        coords = new_coords.flatten().tolist()
        canvas.create_polygon(coords, fill = "red")
        draw_disc(coords[4], coords[5], f.radius, "red")
        draw_disc(coords[10], coords[11], f.radius, "red")

    canvas.update()


def handle_ball_ball_collision(ball1: Ball, ball2: Ball):
    restitution = min(ball1.restitution, ball2.restitution)
    dir = ball2.pos - ball1.pos
    dist = vector_length(dir)
    if (dist == 0.0 or dist > ball1.radius + ball2.radius):
        # no collision
        return

    dir *= (1.0 / dist)     # normalize

    corr = (ball1.radius + ball2.radius - dist) / 2.0
    ball1.pos += dir * -corr
    ball2.pos += dir * corr

    v1 = ball1.vel.dot(dir)
    v2 = ball2.vel.dot(dir)

    m1 = ball1.mass
    m2 = ball2.mass

    new_v1 = (m1 * v1 + m2 * v2 - m2 * (v1 - v2) * restitution) / (m1 + m2)
    new_v2 = (m1 * v1 + m2 * v2 - m1 * (v2 - v1) * restitution) / (m1 + m2)

    ball1.vel += dir * (new_v1 - v1)
    ball2.vel += dir * (new_v2 - v2)


def handle_ball_circle_obstacle_collision(ball: Ball, obstacle: CircleObstacle):
    dir = ball.pos - obstacle.pos
    dist = vector_length(dir)
    if (dist == 0.0 or dist > ball.radius + obstacle.radius):
        # no collision
        return

    dir *= (1.0 / dist)     # normalize

    corr = ball.radius + obstacle.radius - dist
    ball.pos += dir * corr

    vel = ball.vel.dot(dir)
    ball.vel += dir * (obstacle.push_vel - vel)


def handle_ball_flipper_collision(ball: Ball, flipper: Flipper):
    rotated = flipper.rotate(flipper.rest_angle + flipper.rotation * flipper.sign)
    closest = closest_point_on_segment(ball.pos, rotated[5], rotated[2])

    dir = ball.pos - closest
    dist = vector_length(dir)
    if (dist == 0.0 or dist > ball.radius + flipper.radius):
        # no collision
        return

    dir *= (1.0 / dist)     # normalize
    corr = ball.radius + flipper.radius - dist
    ball.pos += dir * corr

    # update velocity
    radius = np.copy(closest)
    radius += (dir * flipper.radius)
    radius -= flipper.pos[5]
    surface_vel = np.array([-radius[1], radius[0]])
    surface_vel *= flipper.current_angular_vel / 35

    v = ball.vel.dot(dir)
    new_v = surface_vel.dot(dir)
    ball.vel += dir * (new_v - v)


def handle_ball_border_collision(ball: Ball, border):
    len_border = len(border)

    # find closest segment
    min_dist = 0.0
    closest = np.array([])
    normal = np.array([])

    for i in range(len_border - 1):
        a = border[i]
        b = border[(i+1)]
        c = closest_point_on_segment(ball.pos, a, b)
        d = ball.pos - c
        dist = vector_length(d)
        if (i == 0 or dist < min_dist):
            min_dist = dist
            closest = c
            ab = a - b
            normal = np.array([-ab[1], ab[0]])  # This is the left-normal
                                                # We need it because we build the Polygonal
                                                # From Counter-Clockwise
                                                # This is the normal "Inside" the Pinball game

    d = ball.pos - closest
    dist = vector_length(d)

    if (d.dot(normal) >= 0.0) and (dist > ball.radius):     
        # if on correct side of border (i.e. inside canvas) and distance from closest point on border to ball is smaller than radius
        return  # no collision

    unit_normal = normal * (1.0 / vector_length(normal))        # normal vector with unit length
    
    # dist < ball.radius, therefore ball is partially out of border
    # move ball so whole ball inside canvas
    ball.pos = closest + unit_normal * ball.radius
    
    # update velocity
    ball.vel -= 2 * (ball.vel.dot(unit_normal)) * unit_normal  # https://math.stackexchange.com/a/13266
    ball.vel *= 0.8     # multiply by constant so that ball loses some velocity when colliding with border, seems more natural to me


def simulate(physics_scene: PhysicsScene):    
    physics_scene.flippers[0].simulate(physics_scene.dt)
    physics_scene.flippers[1].simulate(physics_scene.dt)

    for ball in physics_scene.balls:
        ball.simulate(physics_scene.dt, physics_scene.g)

    for i in range(len(physics_scene.balls)):
        ball = physics_scene.balls[i]
        
        # BROAD PHASE COLLISION DETECTION
        if (ball.pos[0] > cWidth / 2):
            if (ball.pos[1] > cHeight / 2):
                # BOTTOM RIGHT
                handle_ball_circle_obstacle_collision(ball, physics_scene.obstacles[2])
                handle_ball_flipper_collision(ball, physics_scene.flippers[1])
                handle_ball_border_collision(ball, physics_scene.border[3:8])
            else: 
                # TOP RIGHT
                handle_ball_circle_obstacle_collision(ball, physics_scene.obstacles[1])
                handle_ball_border_collision(ball, physics_scene.border[[6, 7, 0]])
        else:
            if (ball.pos[1] > cHeight / 2):
                # BOTTOM LEFT
                handle_ball_circle_obstacle_collision(ball, physics_scene.obstacles[3])
                handle_ball_flipper_collision(ball, physics_scene.flippers[0])
                handle_ball_border_collision(ball, physics_scene.border[:5])
            else:
                # TOP LEFT
                handle_ball_circle_obstacle_collision(ball, physics_scene.obstacles[0])
                handle_ball_border_collision(ball, physics_scene.border[[7, 0, 1]])

        # if more than 2 balls, this needs to be done differently
        #   for j = 0, j < len(balls), j++
        #       if j != i then handle_collision
        for j in range(i+1, len(physics_scene.balls)):
            handle_ball_ball_collision(ball, physics_scene.balls[j])    

    
def update(physics_scene: PhysicsScene):
    while True:
        simulate(physics_scene)
        draw(physics_scene)
        time.sleep(physics_scene.dt)


def main():
    physics_scene = setup_scene()    
    draw(physics_scene)


start_button = tk.Button(window, text='START', font=('arial bold', 18), height=2, width=10,
    bg="black", fg="white", activebackground="green", relief="raised", command=lambda:(update(setup_scene())))
start_button.pack(side=tk.BOTTOM, anchor=tk.S)


if __name__ == "__main__":
    main()

window.mainloop()
