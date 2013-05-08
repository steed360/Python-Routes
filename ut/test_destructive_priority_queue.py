
import unittest
import thirdParty.dest_priority_dictionary

class Desructive_Priority_Dictionary_TestCase ( unittest.TestCase):

  def setUp (self):

    self.dPrDict = thirdParty.dest_priority_dictionary.d_priority_dict ()
    for key in range (10):
      self.dPrDict [10- key] = 10 - key

  def testToDesruction (self):
    self.setUp ()
    l = []
    for i in self.dPrDict:
      l.append (i)
    self.failUnless ( len (self.dPrDict) ==0  )


  def testPriorityOrderingSimple (self):
    ''' 
    Check that the Q correctly reversed it's default order
    '''
    self.setUp ()
    l = []
    for i in self.dPrDict:
      l.append (i)
    self.failUnless ( l == range (1,11) )

  def testDePrioritization (self):

    ''' 
    Normally we'll be lowing the priority of a value (though
    it has to work both ways of course)
    '''

    self.setUp ()
    self.dPrDict[10]=0
    l = []
    for i in self.dPrDict:
      l.append (i)
    self.failUnless ( l == [10,1,2,3,4,5,6,7,8,9] )

  def testDePrioritizationBatch(self):

    ''' 
    Here, reverse (lower) every priority in the Q.
    10->1, 1->10 etc
    '''

    self.setUp ()

    revList = range (10,0,-1)
    for i in range (1,11):
      self.dPrDict [i] = revList [i-1]

    l = []
    for i in self.dPrDict:
      l.append (i)

    expected = range (1,11)
    expected.reverse()
    
    self.failUnless ( l == expected )

  def testUpPrioritizationBatch(self):

    '''
    Increase the prioritizion of the two elements at the end.
    '''

    self.setUp ()
    self.dPrDict [1] = 100
    self.dPrDict [2] = 10001
    
    l = []
    for i in self.dPrDict:
      l.append (i)

    expected = [3,4,5,6,7,8,9,10,1,2]
    self.failUnless ( l == expected )


  def testMultipleUpdates (self):

    '''
    A priority Q is not really supposed to handle updates to priorities. This one
    handles them well but in a strange way (see priority dictionary module) 
    which is worth testing. 
 
    The expected behaviour is that after any amount of updating functionality is as 
    before.

    ''' 

    self.setUp ()

    # updating is pretty quick
    for i in range (1000):
      for j in range (1,11):
        # This will cause numerous calls to heapify
        self.dPrDict [j] = j + i

    # Now do a last update.

    for i in range (1,11):
      self.dPrDict [i] = i
  
    l = []
    for i in self.dPrDict:
      l.append (i)

    expected = range (1,11)
    self.failUnless ( l == expected )


  def tearDown (self):
    self.dPrDict = None

if __name__ == '__main__': unittest.main ()

