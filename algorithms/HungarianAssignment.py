
# HungarianAssignment.py
# Change Log
# 14/08/2012    - Initial development

import logging
import numpy

def HungarianAssignment (  supplyVertexList, demandVertexList , costMatrix):

  '''

  The underlying algorithm, found in Doland/Aldous' "Networks & Algorithms", is fairly involved. 
  The corresponding TSP code which uses this procedure is much more intuitive & pythonic

  Tests / validation in the UT folder.

  Given a cost matrix find a one-one assignment from one set of "demand" nodes to another set 
  of "supply" nodes such that  the total cost over all pairings is minimized. 
 
  NB: The algorithm can be applied in a branch and bound solution to the TSP 
  (see ./TSP.py)
 
  Parameters:
  -----------

  costMatrix :  2D numpy.array of costs in square matrix form (See example)
 
  supplyVertexList, demandvertexList 
                These lists' elements correspond to the elements in the cost matrix  
                TODO: somewhere I have a numpy subclass to handle named indices correctly. 
                TODO: these parameters are not in fact required if a client applications 
                      accepts ordered indices (so remove them, or use them properly)

  Result:
  Returns a solution as a boolean numpy 2D array  

  Examples (not for doctest)

  supply = ['a','b','c','d']
  demand = ['w','x','y','z']
  costMatrix = numpy.array ( [6,12,15,15, 4, 8, 9,11,10, 5, 7, 8,12,10, 6, 9 ]).reshape (4,4)

  >>> costMatrix
  array( [6,12,15,15,\
          4, 8, 9,11,\
         10, 5, 7, 8,\
         12,10, 6, 9 ]).reshape (4,4)

  The best solution for this problem is 28. There are at least two solutions.

  result = HungarianAssignment.HungarianAssignment ( supply, demand, costMatrix) 

  print result
  >>> [ [True  False False False]
        [False False False True]
        [False True  False False]
        [False False True  False]]

  The above matrix demonstrates how graphs are handled generally here.

  print (resultGraph  * costMatrix).sum()
  >>> 28


  '''

  logging.debug ("--- NEW PROB --- with cost matrix ")
  logging.debug ("\n" + str (costMatrix ))
 
  supplyListCosts, demandListCosts, \
  costMatrix, partialGraphMatrix = HA_Step1_ConstructInitialPartialGraph ( costMatrix )

  matrixSize = len(costMatrix)

  # Create an empty 'result' graph. Once there is a True in every row (according to the rules of 
  # the algorithm, we'll have a complete assignment. 
  MATCHEDGraphBoolMatrix = numpy.array ( [False]*matrixSize*matrixSize   ).reshape( matrixSize, matrixSize) 

  i = 0

  while (not _labellingIsComplete(MATCHEDGraphBoolMatrix) ):

    i = i + 1
    logging.debug ("--TSP: Main Loop with iter: " + str (i) )
    logging.debug ("--Current variables are ")
    logState (partialGraphMatrix, MATCHEDGraphBoolMatrix,None, None )    

    demandBreakthrough, supplyLabelsList, demandLabelsList = \
    HA_Step2_LabellingProcedure ( partialGraphMatrix, MATCHEDGraphBoolMatrix )
 
    logging.debug ("Labelling Procedure done. Results are:")
    logState (partialGraphMatrix, MATCHEDGraphBoolMatrix,supplyLabelsList, demandLabelsList )    

    logging.debug ("demandBreakthrough is : " + str (demandBreakthrough))

    if not demandBreakthrough in [-1,None]:

      logging.debug('breakdthrough')

      # This means that there is a demand node which cannot be reached by the solution (i.e. 
      # by the MATCHED graph. Use the logic of an alternating path via the labels to move an
      # edge from the original partial graph to the MATCHED graph. I.e. gradually move towards
      # the solution

      partialGraphMat, MATCHEDGraphMat = HA_Step3_MatchingImprovement \
                                        ( partialGraphMatrix, MATCHEDGraphBoolMatrix, supplyLabelsList, \
                                          demandLabelsList, demandBreakthrough )

      logging.debug('...did matching improvement')


    else:

      logging.debug('..No breakthrough ....')

      # No breakthrough demand node identified but not all supply nodes have 
      # been labelled. It is now necessary to adjust the costs in order to create
      # another edge in the partial graph.

      originalCostMatrix = costMatrix.copy()
    
      lowestCostDelta = _findLowestEdgeCost (supplyLabelsList, demandLabelsList, costMatrix)
      costMatrix = _reviseCostMatrix (lowestCostDelta, costMatrix, supplyLabelsList, demandLabelsList )

      # This procedure will have created at least one more zero in the cost matrix. Locate it and
      # update the partial graph accordingly.  See function doc if its return value seems confusing.

      matrixCellsToUpdate =  _findNewEdgesFromUpdatedCostMatrix ( originalCostMatrix, costMatrix )
      partialGraphMatrix [ matrixCellsToUpdate ] = True

      costMatrix = originalCostMatrix.copy()

  logging.debug ("__ All done with results:")
  logState (partialGraphMatrix, MATCHEDGraphBoolMatrix,supplyLabelsList, demandLabelsList )    
  return MATCHEDGraphMat 

def _findNewEdgesFromUpdatedCostMatrix ( oldCostMatrix, newCostMatrix ):

  '''
  In this program edges in the derived Partial Graph correspond to zeros in the
  cost matrix (following re-allocation of costs to vertices).

  This routine is used in the situation when we have a new cost Matrix. The new CM 
  contains one or more zeros than were present in the prior cost matrix.

  As for the rtn value, it is appropriate for the structure to be as follows.
  ReturnValues = Array [ ( rowIndex1, rowIndex2, .. rowIndexi), ( colIndex1, colIndex2, .. colIndexj)
  
  This is because a 2D matrix can then be updated conveniently as follows: 
  >>> mat [ ReturnValues] = someValue

  '''

  # Arrange things so that only elements containing zeros are deal with.  

  maskedOldCostMatrix = numpy.ma.array ( oldCostMatrix ) 
  maskedOldCostMatrix.mask = maskedOldCostMatrix == 0

  maskedNewCostMatrix = numpy.ma.array ( newCostMatrix ) 
  maskedNewCostMatrix.mask = maskedNewCostMatrix == 0

  return  numpy.where ( maskedNewCostMatrix.mask - maskedOldCostMatrix.mask ) 

def _initialLabellingOfSupplyNodes (MATCHEDGraphBoolMatrix, supplyLabelsList  ):

  '''
  Helper routine to label with a '*' any supply node that does not access the 
  demand nodes via the MATCH graph.
  ''' 
  numNodes = len ( MATCHEDGraphBoolMatrix )

  # Label each supply Label node with a '*' if it is NOT incident with 
  # any edge in MATCHED

  for i in range ( numNodes  ):

    # .where returns here returns a tuple. Each element in it is a list of matching
    # indices. E.g. array ([0,0,0], array([0,1,2]) i.e. a match in row one / cols 0,1,2

    matchedIndices = numpy.where ( MATCHEDGraphBoolMatrix [i:i+1, :] == False ) [0] #[0]row index

    if len ( matchedIndices ) == numNodes  :
      supplyLabelsList [i] = '*'

  return supplyLabelsList

def _labellingIsComplete (MATCHEDGraphBoolMatrix   ):

  numNodes = len ( MATCHEDGraphBoolMatrix) 
  supplyLabelsList = ['-1']*numNodes   

  '''
  Return True if nonde of the supply nodes are  still labelled '*'
  Labelling is complete means that each supply node has been allocated an
  edge in the MATCH graph.
  ''' 

  matches = []

  supplyLabelsList = _initialLabellingOfSupplyNodes (MATCHEDGraphBoolMatrix, supplyLabelsList  )
  for element in supplyLabelsList:	
    if element == '*':  
      matches.append (element)

  return len (matches) == 0

def HA_Step1_ConstructInitialPartialGraph ( costMatrix ):

  '''

    The objective of this step is to re-allocate some of the costs to demand and supply lists.
    
    Returns:
    ( demandListCosts, supplyListCosts, revisedCostMatrix)

    From this step on, forget about vertex names and refer to them by their indices.
    E.g. in the set X [x1,x2,x3,x4], x1 is referred to as 0 and so on.

  '''

  # Transfer row costs
  # costMatrix.min (axis = 1 ) aggregates each ROW to it's minimum value
    
  supplyListCosts = costMatrix.min (axis=1) 

  # Use numpy broadcasting to reduce every row's elemennt by it's row's cost
  costMatrix = ( costMatrix.transpose() - supplyListCosts ).transpose()

  # Transfer column costs 
  demandListCosts = costMatrix.min (axis=0) 

  # Reduce every cols's elemennt by it's cols's cost
  costMatrix = costMatrix - demandListCosts

  # represent a partial graph where each edge is represented as a TRUE
  partialGraphMatrix = costMatrix == 0

  return supplyListCosts, demandListCosts, costMatrix, partialGraphMatrix


def findFirstBreakThroughIndex ( demandLabelsList, MATCHEDGraphBoolMatrix ):

  '''
  Helper function called by : HA_Step2_LabellingProcedure ()

  The labelling process (part of finding the maximum matching) is complete when:
  - A DEMAND vertex whose demand has NOT been satisfied is labelled (a breakthrough)
    (here is meant that the vertex is not connected by the set of MATCH edges, so 
    an improvement is possible)

  returns True or False
   
  ''' 
  numNodes = len ( MATCHEDGraphBoolMatrix )

  labelledDemandIndices =  numpy.where ( numpy.array ( demandLabelsList ) <> -1 )[0]

  # If no labels then no breakthrough, obviously.
  if len ( labelledDemandIndices) == 0 : return None

  # Now check those cols with labels. 
  # If any of these are entirely unconnected via MATCHED graph, there is a breakthrough.
   
  for colIndex in labelledDemandIndices:
    colEdges = MATCHEDGraphBoolMatrix [ :,colIndex:colIndex + 1 ].transpose ().tolist()[0]
    if  colEdges ==  ( [False] * numNodes ):
        return colIndex   
  # No Breakthrough
  return None

def HA_Step2_LabellingProcedure ( partialGraphBoolMatrix, MATCHEDGraphBoolMatrix ):

  '''

  This step is is part of the sub-algorithm which creates a maximum matching
  between supply- and demand-nodes.
  See 318 of  "Networks and Algorithms" by Dolan and Aldous

  TODO This is one step where graph representation by matrix CAN work but may be 
  improved by a memory data structure, e.g. based on sets or dict  

  Params: 

  partialGraphBoolMatrix.  numpy.array.  square "matrix" indicating all potential 
                           paths from demand to supply that have not placed in the
                           MATCHED graph. 

  MATCHEDGraphBoolMatrix   numpy.array. As above but this represents edges classified
                           as MATCHED in the algorithm 

  Returns
  rowLabels    The main outupt which allows a minimum matching to take place in step 3
  colLabels    As above 

  ( the two graphs are not modified by this labelling procedure)    

  TODO - break up into 2 or 3 functions for better testing.
  ''' 

  numNodes = len ( partialGraphBoolMatrix)

  #  We numbers to be valid indices so 0 cannot be used to mean 'empty'

  supplyLabelsList = [ -1 ] *  numNodes
  demandLabelsList = [ -1 ] *  numNodes

  # these are two queues of nodes just labelled, (As compared with the labels themselves, above)
  # Below the Qs are built up and processed. Once exhausted the func. is complete
  newSupplyLabelsQ = []
  newDemandLabelsQ = []

  # Label each supply Label node with a '*' if it is NOT incident with 
  # any edge in MATCHED

  supplyLabelsList = _initialLabellingOfSupplyNodes (MATCHEDGraphBoolMatrix, supplyLabelsList )

  # Debug 
  logging.debug ("Supply labels list: " + str ( supplyLabelsList) )

  # Put the same values into a processing Q. 
  for i in range ( len ( supplyLabelsList) ):
    if supplyLabelsList [i] == '*' : 
      newSupplyLabelsQ.append (i)  

  # Debug 
  logging.debug ("Supply labels list Q: " + str ( newSupplyLabelsQ))
  logging.debug ("Demand labels list Q: " + str ( newDemandLabelsQ))

  # Now continue labelling supply and demand nodes until a break-
  # through is identified.

  # JS modification of 24/08/2012 (See log at top of file)
  numberOfOuterLoops = 0
  
  alreadyLabelledSupply_List = []
  alreadyLabelledDemand_List = []

  # JS 

  while ( (len(newSupplyLabelsQ) > 0) or
          (len(newDemandLabelsQ) > 0)  ):

#    numberOfOuterLoops = numberOfOuterLoops + 1

    logging.debug ( numberOfOuterLoops)


#    if (numberOfOuterLoops >= numNodes * numNodes): 
#      logging.debug ( "All possible labelling complete" )
#      return -1, supplyLabelsList, demandLabelsList

    logging.debug ( "...Supply labels list Q: " + str ( newSupplyLabelsQ)  + " ... "  + str ( supplyLabelsList)  )
    logging.debug ( "...Demand labels list Q: " + str ( newDemandLabelsQ)  + " ... "  + str ( demandLabelsList)  )

    # Process all newly labelled supply nodes

    while (  len (newSupplyLabelsQ) > 0 ):
  
      k = newSupplyLabelsQ.pop ()

      # Label up all nodes in the set of demand nodes 
      # which are linked via the partial graph (but NB: NOT the MATCH graph)
      
      foundDemandNodes = numpy.where ( partialGraphBoolMatrix [k:k+1, :] == True ) [1]
       # ... [1]col index. 

      logging.debug ( "....Found demand nodes: "+ str ( foundDemandNodes) )

      for thisColIndex in foundDemandNodes:

        if not thisColIndex in alreadyLabelledDemand_List:

          alreadyLabelledDemand_List.append (thisColIndex) 
          demandLabelsList [thisColIndex] = k   # This will be used in Matching Improvement func.
          newDemandLabelsQ.append(thisColIndex) # We'll be popping this off in a few lines!

    # Process all new demand nodes

    while (  len (newDemandLabelsQ) > 0 ):

      k = newDemandLabelsQ.pop () 

      # Label up all nodes in the set of supply nodes 
      # which are linked via the partial graph (but NB: NOT the MATCH graph)
      
      foundSupplyNodes = numpy.where ( MATCHEDGraphBoolMatrix [ : , k:k+1] == True ) [0]
      # ... [0]row index
  
      for thisRowIndex in foundSupplyNodes:
        if not thisRowIndex in alreadyLabelledSupply_List:

          supplyLabelsList [thisRowIndex] = k # This will be used in Matching Improvement func.
          newSupplyLabelsQ.append (thisRowIndex) # We'll be popping this off in a few lines!
          alreadyLabelledSupply_List.append ( thisRowIndex )

    # Is there an opportunity to create an alternating path without looping further?
    # If so, we can do the matching improvement now, and try for a "maximum matching" result.

    breakThrough = findFirstBreakThroughIndex ( demandLabelsList, MATCHEDGraphBoolMatrix )

    if breakThrough <> None:
      return breakThrough, supplyLabelsList, demandLabelsList

  # TODO Should we  really get here?

  return None, supplyLabelsList, demandLabelsList


def HA_Step3_MatchingImprovement ( partialGraphBoolMatrix, MATCHEDGraphBoolMatrix, supplyLabels, demandLabels, demandBreakthrough ):
 
  '''
  This procedure will generally add one edge to the MATCHED graph and remove one from the partialGraph.
  It is not a case of simply switching them over. 
  The labelling from Step 2 is used to implement an 'alternating path' which is achieved by backtracking
  through the labels.

  - Starting at the breakthrough node in the demand list (demand unmet by the MATCH edges)
  - Use the supply node label placed on that breakthrough node.
  - Find the label on the supply node and it to a node in the demand node list, as indicated by it's label.
  - Continue like this until you reach a supply node labelled with '*'

  At this point swap all edges that have been travelled on between the two graphs.   

  ''' 

  logging.debug (" *** MATCHING IMPROVEMENT *** ")

  supplyNodeInd = None
  demandNodeInd = demandBreakthrough

  while ( True ):

    # Backtrack from a demand node to the specified supplynode
    supplyNodeInd = demandLabels [demandNodeInd]

    logging.debug ( "supply node ind: " + str ( supplyNodeInd) )
    logging.debug ( "supply labels: " + str ( supplyLabels)  )

    # Make the necessary adjustments to the graphs.
    partialGraphBoolMatrix [supplyNodeInd :supplyNodeInd+1,demandNodeInd:demandNodeInd+1 ] = False
    MATCHEDGraphBoolMatrix [supplyNodeInd :supplyNodeInd+1,demandNodeInd:demandNodeInd+1 ] = True

    if supplyLabels[ supplyNodeInd ] == '*':
      break

    # Still here? Let's move to the next supply node
    demandNodeInd = supplyLabels[ supplyNodeInd ]

    logging.debug ( "demand node ind: " + str ( demandNodeInd) )
    logging.debug (  "demand labels: " + str ( demandLabels)  )
 
    # Make the necessary adjustments to the graphs.
    partialGraphBoolMatrix [supplyNodeInd :supplyNodeInd+1,demandNodeInd:demandNodeInd+1 ] = True
    MATCHEDGraphBoolMatrix [supplyNodeInd :supplyNodeInd+1,demandNodeInd:demandNodeInd+1 ] = False

    # END OF LOOP

  # Presumably the matrices are passed by reference, but worth making it clear that they've changed in place
  return partialGraphBoolMatrix, MATCHEDGraphBoolMatrix


def _extractSubMatrixDeepCopy ( numpy2DArray, requiredRows, requiredCols):

  '''
  Return sub-matrix defined by the row and col. indices provided in the two lists
  ''' 

  return numpy2DArray [ requiredRows , [ [i] for i in requiredCols  ]  ].transpose().copy()


def _findLowestEdgeCost (supplyLabels, demandLabels, costMatrix):

  '''
  This function returns a single integer (delta) which is the lowest cost in the original partial (bipartate) graph
  which
  - starts at a LABELLED supply vertex
  - ends at an UNLABELLED demand vertex
  - has a non-zero current cost.  
  '''

  logging.debug (" *** _findLowestEdgeCost *** ")

  # Convert supplyLabels / demandLabels 
  # From this format :  [ 10, -1, 200, -1 ]  ( -1 meaning unlabelled)
  # To   this format :  [  0    ,    2    ]  ( i.e. a list of labelled indices
  # NB : (for demand labels, it is the opposite:  we need the UNlabelled indices)

  supplyLabelsList     = [i for i in range (0, len(supplyLabels)) if supplyLabels[i] <> -1 ]
  demandUnLabelledList = [i for i in range (0, len(demandLabels)) if demandLabels[i] == -1 ]

  subCostMatrix = _extractSubMatrixDeepCopy ( costMatrix, supplyLabelsList, demandUnLabelledList ) 
  subCostMatrixMin = subCostMatrix.min ()

  if  subCostMatrixMin== 0 : 

    inds =    numpy.where ( subCostMatrix == 0 ) 
    subCostMatrix [ inds ] = subCostMatrix.max () + 1
  return subCostMatrix.min ()


def _reviseCostMatrix (lowestCostFound, costMatrix, supplyNodeLabels, demandNodeLabels ):

  '''
  The purpose of this function is to enable another edge to 
  be produced. By introducing another edge, it may be possible 
  to produce a maximum matching that is in fact a least cost
  assignment.

  d = lowestCostFound

  The steps followed are:

  a) Increase the weight on each supply VERTEX cost by delta  

  b) Decrease the weight on each demand VERTEX cost by delta 

  c) For each edge which joins a labelled supply vertex to an  
     unlabelled demand vertex DECREASE the cost by d
     I.e. Increase the cost of an edge in the MATCHED list, around
     the part of the problem which is incomplete.  

  d) For each edge from an unlabelled supply node to a labelled 
     demand node, INCREASE the current cost by d.

  The vertex weights in parts a) and b) do not seem to be actually
  required elsewhere in the algorithm so are not implemented here.
  
  Vertex weights are useful because they allow the given user costs
  to be re-constructed like so:  c( Si-Dj )  = C (Si) + C (Dj) + c (i,j)

  '''

  logging.debug ( "*** _reviseCostMatrix ***")

  # Find relevant indices in the current cost matrix.
  indicesLabelledSupplyNds = [i for i in range (0, len(supplyNodeLabels)) if supplyNodeLabels[i] <> -1 ]
  indicesLabelledDemandNds = [i for i in range (0, len(demandNodeLabels)) if demandNodeLabels[i] <> -1 ]

  indicesUnLabelledSupplyNds = [i for i in range (0, len(supplyNodeLabels)) if supplyNodeLabels[i] == -1 ]
  indicesUnLabelledDemandNds = [i for i in range (0, len(demandNodeLabels)) if demandNodeLabels[i] == -1 ]

  # Temporarily mask out zeros.
  costMatrixMasked = numpy.ma.array ( costMatrix , mask = costMatrix == 0)

  # Part C - Adjust costs of relevant MATCHED edges 
  lstd_indicesUnLabelledDemandNds = [ [i] for i in indicesUnLabelledDemandNds]

  costMatrixMasked [ indicesLabelledSupplyNds , lstd_indicesUnLabelledDemandNds] = \
                costMatrixMasked [ indicesLabelledSupplyNds , lstd_indicesUnLabelledDemandNds] - lowestCostFound 

  # Part D - Adjust costs of relevant partial graph edges
  lstd_indicesLabelledDemandNds = [ [i] for i in indicesLabelledDemandNds]

  costMatrixMasked [ indicesUnLabelledSupplyNds , lstd_indicesLabelledDemandNds] = \
        costMatrixMasked [ indicesUnLabelledSupplyNds , lstd_indicesLabelledDemandNds] + lowestCostFound 

  costMatrixMasked.mask = False # re-instate the zeros
  logging.debug ('did revised costs')
  return numpy.array (costMatrixMasked)


def logState ( partialGraph, matchedGraph, supplyLabels, demandLabels ):

  logging.debug ("Partial Graph:\n")
  logging.debug (str("\n") + str (partialGraph))

  logging.debug ("Matched Graph:\n")
  logging.debug (str("\n") + str ( matchedGraph))

  logging.debug ("supplyLabels:\n")
  logging.debug (supplyLabels)

  logging.debug ("demandLabels:\n")
  logging.debug (demandLabels)


