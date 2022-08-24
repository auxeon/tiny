from typing import Set
import components as com
from abc import ABC, abstractmethod
from engine import ECS, SSystem
import OpenGL.GL as gl

class SUpDown(SSystem):
  def init(self):
    self.comset:Set[int] = set([com.CPosition, com.CMoveUpDown])
    self.entities:Set[int] = set()

  def update(self, ecs:ECS, dt:float):
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
      gl.glColor3f(1,1,1)
      gl.glBegin(gl.GL_LINE_LOOP)
      gl.glVertex3f(pos.x - 0.05, pos.y - 0.05, 0.0)
      gl.glVertex3f(pos.x + 0.05, pos.y - 0.05, 0.0)
      gl.glVertex3f(pos.x + 0.05, pos.y + 0.05, 0.0)
      gl.glVertex3f(pos.x - 0.05, pos.y + 0.05, 0.0)
      gl.glEnd()

  def shutdown(self):
    self.entities.clear()