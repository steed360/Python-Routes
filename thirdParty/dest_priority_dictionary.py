# Created by JS to enable the "priorityDictionary" to integrate with the shortest path 
# routine.

import priority_dictionary

class d_priority_dict (priority_dictionary.priority_dict):

  # Pasted from :
  # http://code.activestate.com/recipes/117228-priority-dictionary/

  def __iter__(self):

   #Create destructive sorted iterator of priorityDictionary.

    def iterfn():
      while len(self) > 0:
        x = self.smallest()
        yield x
        del self[x]
    return iterfn()


