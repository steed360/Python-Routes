
import unittest
from algorithms import TSP as TSP
import numpy
import heapq
import random
import time

class HungarianAlgorithm_TestCase ( unittest.TestCase):

  def setUp (self):
    self.name = 'HungarianAlgorithm_TestCase'


  def test_findCircuits (self):

    # (1->3, 3-1), (2-4, 4-5, 5-2)
    testMatrix = numpy.array (
      [False,  False,  True,   False, False,
       False,  False,  False,  True,  False,
       True,   False,  False , False,  False,
       False,  False,  False,  False, True,
       False,  True,   False , False, False] ).reshape (5,5)

    res = TSP._findCircuits ( testMatrix )

    self.failUnless ( heapq.heappop ( res ) == [(2,0),(0,2)] )
    self.failUnless ( heapq.heappop ( res ) == [(1,3),(3,4), (4,1)] )


  def testComparableList (self):

    listLong   = TSP.List_LengthComparable ( [1,2,3] )
    listShort  = TSP.List_LengthComparable ( [100,200] )

    self.failUnless ( listLong  > listShort)
    self.failUnless ( listShort < listLong  )
    self.failUnless ( not (listShort == listLong)  )
    self.failUnless ( listLong  >= listShort)
    self.failUnless ( listShort <= listLong  )

  def testProblemClassOne (self):

    costMatrix = numpy.array (
      [  0,   1 ,  1000 ,  3,     2, 1000 , 
         1,   0 ,     3 ,  3,  1000, 1000 , 
      1000,   3 ,  0    ,  5,  1000,    4 ,
         3,   3 ,     5 ,  0,     3,    5 , 
         2, 1000,  1000 ,  3,     0,    7 , 
      1000, 1000,     4 ,  5,     7,    0 ]).reshape (6,6)

    a1 = TSP.AssignmentProblem ( costMatrix , None ) 
    a1.doAssignment ()
 
    self.failUnless ( 16 == a1.getTotalCost () )
    self.failUnless (  3 ==  len (a1.getAllCircuits () )  )
  
    thisConstraint =  [(1,0)]

    childAssignment = TSP.AssignmentProblem (costMatrix, thisConstraint  )
    childAssignment.doAssignment()

    self.failUnless ( 17 == childAssignment.getTotalCost () )

    childAssignment2 = TSP.AssignmentProblem (costMatrix, None )

    childAssignment2.addConstraint ( ( 2 , 5 )  )
    childAssignment2.addConstraint ( ( 0 , 1 )  )

    childAssignment2.doAssignment()

    self.failUnless ( 18 == childAssignment2.getTotalCost () )

    # One last thing to test will placing two problems in a heap
    # cause them to be sorted correctly.

    myHeap = []
    heapq.heappush ( myHeap, childAssignment )  #17
    heapq.heappush ( myHeap, a1 )  # 16
    heapq.heappush ( myHeap, childAssignment2) #18
   
    cheapestAssignment = heapq.heappop ( myHeap )   


    self.failUnless ( cheapestAssignment <> 16)


  def testTSP (self):


    costMatrix = numpy.array (
      [  0,   1 ,  1000 ,  3,     2, 1000 , 
         1,   0 ,     3 ,  3,  1000, 1000 , 
      1000,   3 ,  0    ,  5,  1000,    4 ,
         3,   3 ,     5 ,  0,     3,    5 , 
         2, 1000,  1000 ,  3,     0,    7 , 
      1000, 1000,     4 ,  5,     7,    0 ]).reshape (6,6)


    '''
    costMatrix = numpy.array (
      [  0,   1,   1 ,  3,    2,   1 , 
         1,   0,   3 ,  3,    1,   1 , 
         1,   3,   0 ,  5,    1,   4 ,
         3,   3,   5 ,  0,    3,   5 , 
         2,   1,   1 ,  3,    0,   7 , 
         1,   1,   4 ,  5,    7,   0 ]).reshape (6,6)

    '''

#    result = TSP.TSP ( costMatrix ) 
#    self.failUnless ( result.getTotalCost ()	 == 18 )

    ap = TSP.AssignmentProblem ( costMatrix, None)
    ap.addConstraint ( (5,2) )
 


  def testTSP2 (self):

    costMatrix = numpy.array (
      [  0,   1 ,  4 ,  3,  2, 4 , 
         1,   0 ,  3 ,  3,  4, 4 , 
         4,   3 ,  0 ,  5,  4, 4 ,
         3,   3 ,  5 ,  0,  3, 5 , 
         2,   4,   4 ,  3,  0, 7 , 
         4,   4,   4 ,  5,  7, 0 ]).reshape (6,6)

    '''
    costMatrix = numpy.array (
      [  0,   1,   1 ,  3,    2,   1 , 
         1,   0,   3 ,  3,    1,   1 , 
         1,   3,   0 ,  5,    1,   4 ,
         3,   3,   5 ,  0,    3,   5 , 
         2,   1,   1 ,  3,    0,   7 , 
         1,   1,   4 ,  5,    7,   0 ]).reshape (6,6)

    '''

    print "------------------------------------------"

    result = TSP.TSP ( costMatrix ) 
    self.failUnless ( result.getTotalCost ()	 == 18 )
#    print result.getAllCircuits ()

#    print 'Total Cost: ' + str  ( result.getTotalCost() )


'''
  def testLargeMatrix (self):

    costMatrix = numpy.arange ( 50*50).reshape (50,50)
    for i in range (0, len ( costMatrix )):
      for j in range (0, len ( costMatrix )):
        costMatrix [i:i+1, j:j+1] = 100 * random.random ()
    
#    print "starting le grande " + str ( time.asctime() ) 
    result = TSP.TSP ( costMatrix ) 
    print "finished " + str ( time.asctime() ) 
#    print result.getAllCircuits ()
'''
	
#--------------------

if __name__ == '__main__': unittest.main ()


