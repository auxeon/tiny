import uuid, glfw, time
import OpenGL.GL as gl
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, Set
from dataclasses import dataclass
import constants as consts
from utils import ID
import components as com

@dataclass
class CComponent(ABC):
  ...

class SSystem(ABC):
  def __init__(self:"SSystem"):
    self.entities:Set[int] = set()
    self.comset:Set[int] = set()
  
  @abstractmethod
  def init(self:"SSystem"):
    ...
  @abstractmethod
  def update(self:"SSystem"):
    ...
  @abstractmethod
  def shutdown(self:"SSystem"):
    ...

class ECS:
  def __init__(self:"ECS"):
    self.entgenid = ID(consts.MAXENTS)
    self.sysgenid = ID(consts.MAXSYS)
    self.entarchetypedb:Dict[int, Set[int]] = defaultdict(lambda: set())
    self.sysarchetypedb:Dict[int, Set[int]] = defaultdict(lambda: set())
    self.sys2id:Dict[SSystem(), int] = defaultdict(lambda: None)
    self.id2sys:Dict[int, SSystem()] = defaultdict(lambda: None)
    self.compooldb:Dict[int, List[Any]] = defaultdict(lambda: [])
    self.compoolsz:Dict[int, int] = defaultdict(lambda: 0)
    self.ent2index:Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(lambda: -1))
    self.index2ent:Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(lambda: -1))

  def validate(self:"ECS", entid:int):
    if not self.entgenid.valid(entid):
      raise Exception("invalid entity id")

  def createEntity(self:"ECS") -> int:
    id = self.entgenid.getid()
    if id == consts.MAXENTS:
      raise Exception("max entitiy limit reached cannot create")
    return id

  def destroyEntity(self:"ECS", entid:int):
    self.validate(entid)
    return self.entgenid.retid(entid)

  def setArchetype(self:"ECS", entid:int, atype:Set[int]) -> None:
    self.validate(entid)
    self.entarchetypedb[entid] = atype

  def getArchetype(self:"ECS", entid:int)-> Set[int]:
    self.validate(entid)
    return self.entarchetypedb[entid]

  def hasComponent(self:"ECS", entid:int, componentid:int):
    self.validate(entid)
    return componentid in self.entarchetypedb[entid]

  def addComponent(self:"ECS", entid:int, comtype:Type, componentdata:Any) -> None:
    atype = self.getArchetype(entid)
    comid = com.component2id[comtype]
    if entid in self.ent2index[comid]:
      raise Exception("trying to add pre-existing component")
    pool = self.compooldb[comid]
    sz = self.compoolsz[comid]
    if sz == len(pool):
      pool.extend([None]*(len(pool)*2 + 1))
    index = sz
    self.ent2index[comid][entid] = index
    self.index2ent[comid][index] = entid
    self.compooldb[comid][index] = componentdata
    self.compoolsz[comid] += 1
    self.compooldb[comid] = pool
    atype.add(comid)
    self.setArchetype(entid, atype)
    self.systemUpdateEntityArchetypeChanged(entid, atype)

  def removeComponent(self:"ECS", entid:int, comtype:Type) -> None:
    comid = com.component2id(comtype)
    if entid in self.ent2index[comid]:
      raise Exception("trying to add pre-existing component")
    removeindex = self.ent2index[comid][entid]
    lastindex = self.compoolsz[comid] - 1
    self.compooldb[comid][removeindex] = self.compooldb[comid][lastindex]
    lastent = self.index2ent[comid][lastindex]
    self.ent2index[comid][lastent] = removeindex
    self.index2ent[comid][removeindex] = lastent
    self.ent2index[comid].pop(entid)
    self.index2ent[comid].pop(lastindex)
    self.compoolsz[comid] -= 1
    
  def getComponent(self:"ECS", entid:int, comtype:Type) -> Any:
    comid = com.component2id[comtype]
    if entid not in self.ent2index[comid]:
      raise Exception("component does not exist")
    return self.compooldb[comid][self.ent2index[comid][entid]]
  
  def onEntityDestroy(self:"ECS", entid:int):
    for comtype in com.allcomponents:
      comid = com.component2id(comtype)
      if entid in self.ent2index[comid]:
        self.removeComponent(entid, comtype)
  
  def registerSystem(self:"ECS", systype:Type, comset:Set[Type]):
    if systype in self.sys2id:
      return
    sysid = self.sysgenid.getid()
    if sysid == consts.MAXSYS:
      raise Exception("max systems limit reached cannot register new system")
    self.sys2id[systype] = sysid
    self.id2sys[sysid] = systype
    if sysid in self.sysarchetypedb:
      raise Exception("error assigning system archetype")
    for component in comset:
      if component in com.allcomponents:
        comid = com.component2id[component]
        self.sysarchetypedb[sysid].add(comid)
      else:
        raise Exception("invalid component in system archetypre component id list")

  def systemUpdateEntityArchetypeChanged(self:"ECS", entid:int, newatype:Set[int]):
    for system in self.sys2id.keys():
      sysid = self.sys2id[system]
      sysarchetype = self.sysarchetypedb[sysid]
      if sysarchetype.issubset(newatype):
        system.entities.add(entid)
      else:
        system.entities.discard(entid)

class GraphicsManager:
  windows:Dict[uuid.UUID, Any] = defaultdict(lambda: None)
  running:Dict[uuid.UUID, bool] = defaultdict(lambda: False)

  @classmethod
  def init(cls):
    if not glfw.init():
      raise Exception("could not initialize glfw")

  @classmethod
  def createWindow(cls, id:int, width:int, height:int, title:str):
    window = glfw.create_window(width, height, title, None, None)
    if not window:
      glfw.terminate()
      raise Exception("could not create glfw window")
    GraphicsManager.windows[id], GraphicsManager.running[id] = window, True
    return window

  @classmethod
  def makeWindowCurrent(cls, windowid:int):
    glfw.make_context_current(GraphicsManager.windows[windowid])

class Tiny(ABC):
  running = False
  updatefuncs = defaultdict(lambda: None)
  shutdownfuncs = defaultdict(lambda: None)
  expectedtime = 1/consts.MAXFPS if consts.MAXFPS != 0 else 0
  frametime = 0.0
  toremove = []
  fpsbufsz = 10
  ri = 0
  wi = fpsbufsz - 1
  fpsrolling = [0]*fpsbufsz
  fps = 0

  def __init__(self:"Tiny", w:int, h:int, title:str):
    self.id:uuid.UUID = uuid.uuid4()
    GraphicsManager.init()
    self.window:Any = GraphicsManager.createWindow(self.id, w, h, f"{title}")
    glfw.make_context_current(self.window)
    GraphicsManager.windows[self.id] = self.window
    GraphicsManager.running[self.id] = True
    Tiny.updatefuncs[self.id] = self.update
    Tiny.shutdownfuncs[self.id] = self.shutdown
    if not Tiny.running:
      Tiny.running = True
    self.init()
    self.title = title

    
  @classmethod
  def __shutdown(cls, keylist:List[uuid.UUID]):
    for key in keylist:
      Tiny.shutdownfuncs[key]()
      if key in GraphicsManager.windows:
        glfw.destroy_window(GraphicsManager.windows[key])
        GraphicsManager.windows.pop(key)
      if key in GraphicsManager.running:
        GraphicsManager.running.pop(key)
      if len(GraphicsManager.running) == 0:
        Tiny.running = False

  @classmethod
  def run(cls):
    if not Tiny.running:
      Tiny.__shutdown(GraphicsManager.running.keys())
    cls.toremove:List[int] = []
    while Tiny.running:
      cls.fpsrolling[cls.wi] = cls.frametime
      cls.fps += (cls.fpsrolling[cls.wi] - cls.fpsrolling[cls.ri])/(cls.fpsbufsz-1)
      cls.wi = (cls.wi + 1) % (cls.fpsbufsz)
      cls.ri = (cls.ri + 1) % (cls.fpsbufsz)
      cls.t0 = glfw.get_time()
      for id in GraphicsManager.windows.keys():
        window = GraphicsManager.windows[id]
        GraphicsManager.makeWindowCurrent(id)
        gl.glClearColor(0,0,0,1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        glfw.poll_events()
        Tiny.updatefuncs[id](cls.frametime)
        glfw.swap_buffers(window)
        if glfw.window_should_close(window):
          cls.toremove.append(id)
      cls.frametime = glfw.get_time() - cls.t0
      while cls.frametime < cls.expectedtime and consts.MAXFPS != 0:
        cls.frametime = glfw.get_time() - cls.t0
      Tiny.__shutdown(cls.toremove)
      cls.toremove.clear()
  
  @abstractmethod
  def init(self) -> None:
    ...
  @abstractmethod
  def update(self, dt:float) -> None:
    ...
  @abstractmethod
  def shutdown(self) -> None:
    ...