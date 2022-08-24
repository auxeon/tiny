class ID:
  def __init__(self:"ID", maxids:int):
    self._maxids = maxids
    self._releasedids = set()
    self._activeids = set()
    self._curid = 0

  def getid(self:"ID") -> int:
    id = self._maxids
    if len(self._releasedids) > 0:
      id = self._releasedids.pop()
    elif self._curid < self._maxids:
      id = self._curid
      self._curid += 1
    self._activeids.add(id)
    return id
  
  def retid(self:"ID", id:int) -> bool:
    if not self.valid(id):
      return False
    l0 = len(self._activeids)
    self._activeids.discard(id)
    changed = l0 != len(self._activeids)
    self._releasedids.add(id) if changed else ... 
    return True if changed else False
  
  def valid(self:"ID", id:int) -> bool:
    return id > -1 and id < self._maxids and id in self._activeids

if __name__ == "__main__":
  idgen = ID(10)
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.valid(2))
  print(idgen.retid(2))
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())
  print(idgen.getid())