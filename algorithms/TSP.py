
# TSP

import numpy
import heapq
import algorithms.HungarianAssignment as HA

''' 

This algorithm finds a best available solution to the 
"(unconstrained) Travelling Salesman Problem" (TSP).

Given a cost matrix representing a complete bi-directional graph between nodes, find 
a circuit starting at any node such that each other node is visited only one in the 
at the least possible cost.

This implemention is probably the simplest of the branch and bound methods and relies on 
the availability of a least cost assignment procedure.

It does not use a heuristic and so will not scale far beyond 100 nodes in the current form.
 
See the doc below on AssignmentProblem and TSP for a description of the procedure.
 
>>>

'''

class List_LengthComparable (list):

  ''' 
  Utility subclass of list, in which the comparison 'magic methods' are over-loaded so 
  as to compare the NUMBER OF ELEMENT in the list instead of the first different element.

  The class was created to allow lists to be pushed onto heapq, which is useful for the
  branch and bound algorithm implemented in the TSP implementation in this module.
  
  ''' 

  def __gt__(self, other):
    return len(self) > len(other)  
  def __lt__(self, other):
    return len(self) < len(other)  
  def __eq__(self, other):
    return len(self) == len(other)  
  def __ge__(self, other):
    return len(self) >= len(other)  
  def __le__(self, other):
    return len(self) <= len(other)  
 
def _findCircuits ( assignedTrips ) :

  '''

  AssignedTrips is a boolean square matrix where a True value indicates a 
  trip. There should be only one True value in each row (i.e. from each node).  

  It returns a (min) priority Q (using heapq) a list of the circuits, so that
  they are popped reverse order of length (shortest circuit first).

  In fact each circuit in the list is a list but of class List_LengthComparable.
  This means that l1 [1,2,3,4] < l2 [100,200] because l1 is shorter. Hence it 
  will be popped of the priority Q first.

  '''

  def _listIntoTuples ( inList ):
    '''
    Given a list [1,2,3,4], 
    return pairs of tuples e.g. [(1,2),(2,3),(3,4)]
    ''' 
    return [(inList[i], inList[i+1]) for i in  range (0, len (inList)-1 ) ]

  resultHeap = []

  nextRow       =  int ( numpy.where  (assignedTrips[0:1,:] == True )[1]  )
  newCircuit    =  List_LengthComparable ([])
  availableRows =  range (0,  len (assignedTrips )  ) # i.e [1,2,..,n-1] 

  # for counter in [1,2,..,n]
  for counter in range ( 1, len ( assignedTrips ) + 1   ):  

    newCircuit.append ( nextRow )
    availableRows.remove ( nextRow)

    nextRow    = int ( numpy.where  (assignedTrips[nextRow:nextRow+1,:] == True )[1]  )
    if nextRow == newCircuit [0]:
      newCircuit.append (nextRow)
      heapq.heappush ( resultHeap  , List_LengthComparable (_listIntoTuples (newCircuit)) )
      newCircuit = List_LengthComparable ([])
      if len ( availableRows ) > 0 : 
        nextRow =  availableRows [0]

  return resultHeap

class AssignmentProblem:

  '''
  
  An assignment problem refers to the Hungarian Assignment problem 
  (see algorithms.HungarianAssignment for full details.

  The class is instantiated with:

  - originalCostMatrix.  
    A square matrix of costs which is handed to the assignment procedure
    nb: diagonals will be set to (something like) infinity during 
    initialization.

  - startingConstraints:
    A list of tuples pointing to a cell. Each of these corresponds to a 
    cell in the costMatrix. That cell will be set to infinity before the 
    assignment procedure is undertaken.

  Different instances of AssignmentProblem can be compared because __eq__, 
  __gt__ etc have been over-ridden to use self.getTotalCost () which provides
  the total cost of this assignment. This means that different assignments
  can be compared, or queued, very easily.

  Before running an assignment, it is normally necessary to add one more 
  constraint. This can be done with the addConstraint () method.
  
  Apart from the total cost, the result of an assignment of interest is the
  circuits produced. There is an obvious method for this but nb that the 
  list of circuits produced is in fact a heapq priority list so that  

  It is possible to set the result (total cost) to infinity. This is so that, 
  once it's children are processed, this Assignment can be de-prioritized (i.e.
  will always be higher than anything else). 

  '''

  def __init__ (self, originalCostMatrix, startingConstraints = None):

    self.constraints = []
    self.costMatrix = originalCostMatrix
    self.matrixLen  = len (self.costMatrix)

    self.infinity   = 100000000
    self.setDiagonalInfinite()
  
    if (startingConstraints <> None and type(startingConstraints == 'list')):
       self.constraints = startingConstraints [:]

    self.booleanMatrix = numpy.array ( [False]*(self.matrixLen*self.matrixLen)).reshape (self.matrixLen,self.matrixLen)

    self.hasInfiniteTotalCost   = False

  def setDiagonalInfinite (self):
    for i in range ( self.matrixLen ):
      self.costMatrix [i:i+1,i:i+1] = self.infinity
 
  def doAssignment(self):
    costMatrixCopy = self.costMatrix.copy()

    for thisConstraint in self.constraints :
      xIndex =  int (thisConstraint [0])    
      yIndex =  int (thisConstraint [1])    
      costMatrixCopy [ xIndex:xIndex+1, yIndex:yIndex + 1  ] = self.infinity
       
#    print " "
#    print costMatrixCopy

    indices = range (0,  self.matrixLen  )
    self.booleanMatrix = HA.HungarianAssignment ( indices, indices, costMatrixCopy)

  def getTotalCost (self):
    if self.hasInfiniteTotalCost:
      return self.infinity
    return (self.costMatrix * self.booleanMatrix ).sum()

  def getAllCircuits (self):
    return _findCircuits ( self.booleanMatrix ) 

  def getSmallestCircuit (self):
    return _findCircuits ( self.booleanMatrix )[0] 

  def addConstraint ( self, constraintTuple):
    self.constraints.append (constraintTuple)

  def getAllConstraints (self):
    return self.constraints

  def setTotalCostInfinite (self):
    self.hasInfiniteTotalCost = True

  def getNumberOfNodes (self):
    return self.matrixLen

  # Magic functions for incorporation in the priority Q.
  def __gt__(self, other):
    return self.getTotalCost > other.getTotalCost ()  
  def __lt__(self, other):
    return self.getTotalCost < other.getTotalCost ()
  def __eq__(self, other):
    return self.getTotalCost == other.getTotalCost ()  
  def __ge__(self, other):
    return self.getTotalCost >= other.getTotalCost ()  
  def __le__(self, other):
    return self.getTotalCost <= other.getTotalCost () 

def TSP (costMatrix):

  '''

  - This is a branch and bound implementation of the TSP. 

  - This works by utilizing the least cost assignment procedure which 
    returns multiple mini-circuits. 

  - By systematically increasing the costs on edges in the mini-circuits,
    the circuits coalesce into larger ones. 

  ''' 


  currentAssignmentProblem = AssignmentProblem ( costMatrix )
  currentAssignmentProblem.doAssignment ()

  if (len ( currentAssignmentProblem.getAllCircuits ()  )  == 1   ):
    return currentAssignmentProblem

  subProblemsOrderedByCost = []

  lowestCost = 1000000000000000000
  minCostProb = None

  while (True):

    if len ( subProblemsOrderedByCost ) > 0:
     currentAssignmentProblem  = heapq.heappop ( subProblemsOrderedByCost )

     if currentAssignmentProblem.getTotalCost () > lowestCost:
       # Our lowest unconstrained problem is better than our best 
       # constrained solution. No further branching needed.

       return minCostProb

    allCircuitsList = currentAssignmentProblem.getAllCircuits ()
    smallestCircuitTuplesList = allCircuitsList [0]

    while (len ( smallestCircuitTuplesList) > 0):
  
      # In turn, make infinite each of the arcs in the first circuit

      thisTuple = smallestCircuitTuplesList.pop ()

      childAssignment = AssignmentProblem ( currentAssignmentProblem.costMatrix, 
                                            currentAssignmentProblem.getAllConstraints() )

      childAssignment.addConstraint ( thisTuple ) 
      childAssignment.doAssignment ()

      if ( len ( childAssignment.getAllCircuits () ) == 1 ):

        # We have found a solution, this may be THE solution
        # once all searching is complete.
 
        if childAssignment.getTotalCost () < lowestCost:
          print "lowest cost set"
          lowestCost  = childAssignment.getTotalCost () 
          minCostProb = childAssignment

      heapq.heappush (  subProblemsOrderedByCost , childAssignment ) 


