from typing import Set
import components as com
from abc import ABC, abstractmethod
from engine import ECS, SSystem
import OpenGL.GL as gl

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