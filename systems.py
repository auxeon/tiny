from typing import Set
import components as com
from engine import ECS, SSystem
import OpenGL.GL as gl
import random, glfw

class SSquareNoisyController(SSystem):
  def __init__(self, window, speed):
    super().__init__()
    self.window = window
    self.speed = speed

  def init(self):
    self.comset:Set[int] = set([com.CPosition, com.CRectangle, com.CColor])
    self.entities:Set[int] = set()

  def update(self, ecs:ECS, dt:float):
    dx = self.speed * (glfw.get_key(self.window, glfw.KEY_RIGHT) - glfw.get_key(self.window, glfw.KEY_LEFT))
    dy = self.speed * (glfw.get_key(self.window, glfw.KEY_UP) - glfw.get_key(self.window, glfw.KEY_DOWN))
    for entid in self.entities:
      pos:com.CPosition = ecs.getComponent(entid, com.CPosition)
      color:com.CColor = ecs.getComponent(entid, com.CColor)
      rect:com.CRectangle = ecs.getComponent(entid, com.CRectangle)
      pos.x = pos.x + dx*dt
      pos.y = pos.y + dy*dt
      gl.glBegin(gl.GL_QUADS)
      gl.glColor3f(color.r, color.g, color.b)
      hh0 = rect.h/2
      hw0 = rect.w/2
      ox = (hw0, hw0, -hw0, -hw0)
      oy = (-hh0, hh0, hh0, -hh0)
      rx = random.random()/100 
      ry = random.random()/100 
      for i in range(4):
        gl.glVertex3f(pos.x + rx + ox[i], pos.y +ry + oy[i], 0)
      gl.glEnd()

  def shutdown(self):
    self.entities.clear()

class SLeftRight(SSystem):
  def init(self):
    self.comset:Set[int] = set([com.CPosition, com.CMoveLeftRight])
    self.entities:Set[int] = set()

  def update(self, ecs:ECS, dt:float):
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_LINE)
    gl.glBegin(gl.GL_QUADS)
    for entid in self.entities:
      pos:com.CPosition = ecs.getComponent(entid, com.CPosition)
      move:com.CMoveLeftRight = ecs.getComponent(entid, com.CMoveLeftRight)
      if move.goingup:
        if move.uptime > 0:
          move.uptime -= dt
        else:
          move.uptime = move.halfduration
          move.goingup = False
      else:
        if move.downtime > 0:
          move.downtime -= dt
        else:
          move.downtime = move.halfduration
          move.goingup = True
      pos.x = pos.x + move.upspeed*dt if move.goingup else pos.x - move.downspeed*dt
      gl.glVertex3f(pos.x - 0.05, pos.y - 0.05, 0.0)
      gl.glVertex3f(pos.x + 0.05, pos.y - 0.05, 0.0)
      gl.glVertex3f(pos.x + 0.05, pos.y + 0.05, 0.0)
      gl.glVertex3f(pos.x - 0.05, pos.y + 0.05, 0.0)
    gl.glEnd()

  def shutdown(self):
    self.entities.clear()

class SUpDown(SSystem):
  def init(self):
    self.comset:Set[int] = set([com.CPosition, com.CMoveUpDown])
    self.entities:Set[int] = set()

  def update(self, ecs:ECS, dt:float):
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_LINE)
    gl.glBegin(gl.GL_QUADS)
    for entid in self.entities:
      pos:com.CPosition = ecs.getComponent(entid, com.CPosition)
      move:com.CMoveUpDown = ecs.getComponent(entid, com.CMoveUpDown)
      if move.goingup:
        if move.uptime > 0:
          move.uptime -= dt
        else:
          move.uptime = move.halfduration
          move.goingup = False
      else:
        if move.downtime > 0:
          move.downtime -= dt
        else:
          move.downtime = move.halfduration
          move.goingup = True
      pos.y = pos.y + move.upspeed*dt if move.goingup else pos.y - move.downspeed*dt
      gl.glVertex3f(pos.x - 0.05, pos.y - 0.05, 0.0)
      gl.glVertex3f(pos.x + 0.05, pos.y - 0.05, 0.0)
      gl.glVertex3f(pos.x + 0.05, pos.y + 0.05, 0.0)
      gl.glVertex3f(pos.x - 0.05, pos.y + 0.05, 0.0)
    gl.glEnd()

  def shutdown(self):
    self.entities.clear()