
import unittest
import thirdParty.shortestPath

class ShortestPath_TestCase ( unittest.TestCase):

  def setUp (self):

    self.graph = { 'a': {'b': 1   },  
                   'b': {'d': 1.5,
                         'c': 1   },
                   'c': {'d': 1   }
                  }


  def testRoute1 (self):

    route = thirdParty.shortestPath.shortestPath ( self.graph, 'a', 'd')
    self.failUnless ( route == ['a','b','d']	  )


#  def testNonRoute (self):
#    route = thirdParty.shortestPath.shortestPath ( self.graph, 'd', 'a')
#    self.failUnless ( route == []  )

if __name__ == '__main__': unittest.main ()

