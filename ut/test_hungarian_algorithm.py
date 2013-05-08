
import unittest
from algorithms import HungarianAssignment
import numpy

class HungarianAlgorithm_TestCase ( unittest.TestCase):

  def setUp (self):
	
    self.costMatrix = numpy.array ([6,12,15,15,\
                                    4, 8, 9,11,\
                                   10, 5, 7, 8,\
                                   12,10, 6, 9 ]).reshape (4,4)

#  def _test1():
  def testStepOne_AssignWeightsToVertices (self):

    demandCosts, supplyCosts,costMatrixRes, partialGraphMat = \
    HungarianAssignment.HA_Step1_ConstructInitialPartialGraph (self.costMatrix) 

    self.failUnless  ( list ( demandCosts)  == [6,4,5,6] ) # The minimum values in each row

    self.failUnless  ( list ( supplyCosts)  == [0,0,0,3] ) 

    correctCostMatrix = numpy.array ( [0,6,9,6,0,4,5,4,5,0,2,0,6,4,0,0] ).reshape(4,4)

    self.failUnless  ( ( costMatrixRes  - correctCostMatrix ).sum() ==0) 

    correctpartialGraphMat = numpy.array ([True, False, False, False, 
                                           True, False, False, False,
                                           False,True,  False, True,  
                                           False,False, True,  True] ).reshape(4,4)

    self.failUnless  ( ( correctpartialGraphMat - partialGraphMat ).sum() ==0) 


#  def _test1():
  def testfoundBreakThroughOne (self):
    '''
    This will pass because the last demand node is not attached to any 
    edges in the MATCHED graph : it's a breakthrough...

    ''' 

    demandLabelsList = [-1] * 4
    demandLabelsList [3] = 0

    MATCHEDGraphBoolMatrix = numpy.array ( [False]*16).reshape(4,4)

    res = HungarianAssignment.findFirstBreakThroughIndex ( demandLabelsList, MATCHEDGraphBoolMatrix ) 
    self.failUnless ( res == 3 )
  
#  def _test1():  
  def testfoundBreakThroughTwo (self):
    '''
    This should fail because there NO labelled demand vertices to consider.

    ''' 

    demandLabelsList = [-1] * 4

    MATCHEDGraphBoolMatrix = numpy.array ( [False]*16).reshape(4,4)
    res = HungarianAssignment.findFirstBreakThroughIndex ( demandLabelsList, MATCHEDGraphBoolMatrix ) 
    self.failUnless ( res==None )

#  def _test1():
  def testfoundBreakThroughThree (self):
    '''
    This will fail because although there are labelled demand vertices, 
    edges in graph MATCHED do in fact connect to both of them. 

    ''' 

    demandLabelsList = [-1] * 4
    demandLabelsList [0] = 0
    demandLabelsList [3] = 1

    MATCHEDGraphBoolMatrix = numpy.array ( [False]*16).reshape(4,4) 
    MATCHEDGraphBoolMatrix [ 0:1 , 0:1  ] = True 
    MATCHEDGraphBoolMatrix [ 0:1 , 3:4  ] = True 

    res = HungarianAssignment.findFirstBreakThroughIndex ( demandLabelsList, MATCHEDGraphBoolMatrix ) 
    self.failUnless ( res==None )

#  def _test1():
  def testStepTwo_LabellingProcedure_One (self):

    '''
    Test a standard case.
    ''' 

    partialGraphMat = numpy.array ([True, True,  False,  False, 
                                    False,False, False, False,
                                    False,True,  False,  False,  
                                    False,False, True,  False] ).reshape(4,4)

    MATCHEDGraphMat  = numpy.array ( [False]*16 ).reshape (4,4)

    breakThrough, supplyLabels, demandLabels = \
    HungarianAssignment.HA_Step2_LabellingProcedure ( partialGraphMat, MATCHEDGraphMat )
  
    correctSupplyLabels = ['*']*4
    self.failUnless ( correctSupplyLabels == supplyLabels )

    correctDemandLabels1 = [0,2,3, -1]
    correctDemandLabels2 = [0,0,3, -1]

    self.failUnless ( correctDemandLabels1 == demandLabels or
                      correctDemandLabels2 == demandLabels )

    self.failUnless ( breakThrough in [ 0,2,3] )

#  def _test1():
  def testStepTwo_LabellingProcedure_Two (self):

    '''
    Test an involved  e.g. from the text book (see page 307)
    There can only be one break-through demand vertex found here
    and that is demand node index 2. 

    Also, the only supply labelling possible is [0,1,'*',3]
    There are different possibilities for the demand vertex labelling.

    Note that this problem requires two iterations of the main labelling loop
    before a breakthrough vertex emerges.
    ''' 

    partialGraphMat = numpy.array ([False, False, False, False, 
                                    False, False, True,  False,
                                    True,  True,  False, True,  
                                    False, True,  True,  False] ).reshape(4,4)

    MATCHEDGraphMat = numpy.array ([True, False, False,  False, 
                                    False, True, False,  False,
                                    False, False, False, False,
                                    False, False, False, True] ).reshape(4,4)

    breakThrough, supplyLabels, demandLabels = \
    HungarianAssignment.HA_Step2_LabellingProcedure ( partialGraphMat, MATCHEDGraphMat )
   

    self.failUnless ( breakThrough == 2) 
    self.failUnless ( supplyLabels == [0,1,'*',3]) 


#  def _test1():
  def _testHA_Step3_MatchingImprovement_One (self):

    '''
    Test that graph "matrices" are correctly modified
    There should be only one result to this given the inputs.

    Add to MATCH Graph (and remove from partial Graph)
    x2,y1 ;  x1,y2

    Add to partial Graph (and remove from MATCH graph)
    x1,y1   
    ''' 

    partialGraphMat = numpy.array ([False, False, False, False, 
                                    False, False, True,  False,
                                    True,  True,  False, True,  
                                    False, True,  True,  False] ).reshape(4,4)

    MATCHEDGraphMat = numpy.array ([True, False, False,  False, 
                                    False, True, False,  False,
                                    False, False, False, False,
                                    False, False, False, True] ).reshape(4,4)

    demandLabels = [2, 3, 3, 2] 
    supplyLabels = [0,1,'*',3]
    demandBreakthrough = 2
 
    a,b = HungarianAssignment.HA_Step3_MatchingImprovement \
    ( partialGraphMat, MATCHEDGraphMat, supplyLabels, demandLabels, demandBreakthrough )

    # TODO complete the test!


#  def _test1():
  def testLabellingIsComplete (self  ):
    MATCHEDGraphMat = numpy.array ([True, False, False,  False, 
                                    False, True, False,  False,
                                    False, False, True, False,
                                    False, False, False, True] ).reshape(4,4)


    res = HungarianAssignment._labellingIsComplete (MATCHEDGraphMat  )
    
    self.failUnless ( res == True)
    
#  def _test1():



  def testExtractSubMatrix ( self ) : 
  
   numpy2DArray = numpy.arange (16).reshape (4,4) 
   requiredRows  = [0,1]
   requiredCols  = [2,3]

   resultMatrix = HungarianAssignment._extractSubMatrixDeepCopy ( numpy2DArray, requiredRows, requiredCols)

   self.failUnless ( resultMatrix.sum () == 18)

  def test_findLowestEdgeCost (self):

    supplyLabels = [ 10,-1,10 ]
    demandLabels = [ -1,10,10  ]
  
    costMatrix = numpy.arange ( 9 ).reshape ( 3,3)

    lowestCost = HungarianAssignment._findLowestEdgeCost (supplyLabels, demandLabels, costMatrix)

    self.failUnless  ( lowestCost == 6)

  def test_findNewEdgesFromUpdatedCostMatrix (self):

    oldCostMatrix = numpy.array ( [ 0,1,1,0 ] ).reshape(2,2)
    newCostMatrix = numpy.array ( [ 0,1,0,0 ] ).reshape(2,2)


    result =  HungarianAssignment._findNewEdgesFromUpdatedCostMatrix ( oldCostMatrix, newCostMatrix )


    testMat = numpy.arange (4).reshape (2,2)
    testMat [result] = 1000

    self.failUnless ( testMat[1:2, 0:1] == 1000 )

  def test_reviseCostMatrix (self):
  
    costMatrix =self.costMatrix

    a, b, costMatrix2, partialGraphMatrix = HungarianAssignment.HA_Step1_ConstructInitialPartialGraph ( costMatrix ) 

    supplyLabels = [0,'*',-1,-1]
    demandLabels = [1,-1,-1,-1]

    delta = HungarianAssignment._findLowestEdgeCost (supplyLabels, demandLabels, costMatrix2)

    self.failUnless ( delta == 4) # see page 320 of 'Networks and Algorithms'

    revCostMatrix = HungarianAssignment._reviseCostMatrix (delta, costMatrix2, supplyLabels, demandLabels )

    self.failUnless ( revCostMatrix.sum () == 35)

  def testHungarianAssignment (self):

    sl = range ( len (self.costMatrix )) 
    dl = range ( len (self.costMatrix )) 

    resultGraph = HungarianAssignment.HungarianAssignment (  sl, dl , self.costMatrix)

    self.failUnless (  (self.costMatrix * resultGraph ).sum()  == 28 ) 

#--------------------
if __name__ == '__main__': unittest.main ()


