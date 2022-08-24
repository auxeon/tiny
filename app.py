from collections import defaultdict
import time, random, glfw
from typing import List, Set, Dict, Any, Type
import OpenGL.GL as gl
import components as com
import systems as syz
import constants as consts
from engine import Tiny, GraphicsManager, ECS
import imgui
from imgui.integrations.glfw import GlfwRenderer

class GUIScreen0(Tiny):
  """
  using imgui will limit to single screen since imgui uses a singleton shared context
  """
  def __init__(self, w: int, h: int, title: str):
    super().__init__(w, h, title)

  def init(self) -> None:
    self.imguictx = imgui.create_context()
    self.implimgui = GlfwRenderer(self.window)
    self.numrects = 100
    self.colors = tuple(com.CColor(random.random(), random.random(), random.random(), 1.0) for x in range(self.numrects))
    self.rectangles = tuple(com.CRectangle(random.random()/10, random.random()/10) for x in range(self.numrects))
    self.positionsdb = tuple(com.CPosition(random.random()*2.0 - 1.0, random.random()*2.0 - 1.0, 0) for x in range(self.numrects*10))
    self.expectedtime = int(1/consts.MAXFPS*1e9)
    self.start = 0

  def update(self, dt:float) -> None:
    self.implimgui.process_inputs()
    self.t0 = time.monotonic_ns()
    if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
      self.start = (self.start + 1) % 10
      self.positions = self.positionsdb[self.start*self.numrects:self.start*self.numrects+self.numrects]
      GraphicsManager.running[self.id] = True
    else:
      GraphicsManager.running[self.id] = False

    if GraphicsManager.running[self.id]:
      for x in range(self.numrects):
        gl.glColor3f(self.colors[x].r, self.colors[x].g, self.colors[x].b)
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex3f(self.positions[x].x, self.positions[x].y, 0.0)
        gl.glVertex3f(self.positions[x].x + self.rectangles[x].w, self.positions[x].y, 0.0)
        gl.glVertex3f(self.positions[x].x + self.rectangles[x].w, self.positions[x].y + self.rectangles[x].h, 0.0)
        gl.glVertex3f(self.positions[x].x + 0.0, self.positions[x].y + self.rectangles[x].h, 0.0)
        gl.glEnd()
      
    imgui.new_frame()
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("Options", True):
            clicked_quit, selected_quit = imgui.menu_item(
                "Quit", 'Cmd+Q', False, True
            )
            if clicked_quit:
                Tiny.toremove.append(self.id)
                # Tiny.running = False
            imgui.end_menu()
        imgui.end_main_menu_bar()
    imgui.end_frame()
    imgui.render()
    self.implimgui.render(imgui.get_draw_data())
    if GraphicsManager.running[self.id]:
      frametime = (time.monotonic_ns() - self.t0)
      if frametime < self.expectedtime:
        time.sleep(1/1e9 * (self.expectedtime - frametime))

  def shutdown(self) -> None:
    self.rectangles *= 0
    self.positionsdb *= 0
    self.colors *= 0
    imgui.destroy_context(self.imguictx)
  
class GameScreen0(Tiny):
  def __init__(self, w: int, h: int, title: str):
    super().__init__(w, h, title)
    self.ecs = ECS()
    self.systems = [syz.SUpDown()]
    self.ecs.registerSystem(self.systems[0], self.systems[0].comset)
    for s in self.systems:
      s.init()
    self.e0 = self.ecs.createEntity()
    self.ecs.addComponent(self.e0, com.CPosition, com.CPosition(
      0.0,-0.6,0.0
    ))
    self.ecs.addComponent(self.e0, com.CMoveUpDown, com.CMoveUpDown(
      1.0,
      1.0,
      1.0,
      1.0,
      1.0,
      True,
    ))
    self.e0 = self.ecs.createEntity()
    self.ecs.addComponent(self.e0, com.CPosition, com.CPosition(
      -0.2,-0.6,0.0
    ))
    self.ecs.addComponent(self.e0, com.CMoveUpDown, com.CMoveUpDown(
      1.0,
      1.0,
      1.0,
      1.5,
      1.5,
      True,
    ))
    self.t0 = time.monotonic_ns()
    self.fixedupdate = True
  
  def init(self) -> None:
    ...
    
  def update(self, dt:float) -> None:
    _dt = 1/consts.MAXFPS if self.fixedupdate else dt
    for s in self.systems:
      s.update(self.ecs, _dt)
    self.t0 = time.monotonic_ns()

  def shutdown(self) -> None:
    for s in self.systems:
      s.shutdown()

if __name__ == "__main__":
  # can only have a single gui screen because pyimgui uses a singleton imgui context
  guiscreen = (GUIScreen0(800, 800, "GUI Screen"))
  gamescreens = (
    GameScreen0(700, 700, "Game Screen"),
    GameScreen0(700, 700, "Game Screen"),
    GameScreen0(700, 700, "Game Screen"),
  )
  Tiny.run()