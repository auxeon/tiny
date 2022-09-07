from dataclasses import dataclass
from engine import CComponent

@dataclass
class CPosition(CComponent):
  x:float
  y:float
  z:float

@dataclass
class CRotation(CComponent):
  qx:float
  qy:float
  qz:float
  qw:float

@dataclass
class CScale(CComponent):
  sx:float
  sy:float
  sz:float

@dataclass
class CColor(CComponent):
  r:float
  g:float
  b:float
  a:float

@dataclass
class CHealth(CComponent):
  min:float
  max:float
  val:float

@dataclass
class CRectangle(CComponent):
  h:float
  w:float

@dataclass
class CMoveUpDown(CComponent):
  halfduration:float = 1.0
  uptime:float = halfduration
  downtime:float = halfduration
  upspeed:float = 0.005
  downspeed:float = 0.005
  goingup:bool = True


@dataclass
class CMoveLeftRight(CComponent):
  halfduration:float = 1.0
  uptime:float = halfduration
  downtime:float = halfduration
  upspeed:float = 0.005
  downspeed:float = 0.005
  goingup:bool = True