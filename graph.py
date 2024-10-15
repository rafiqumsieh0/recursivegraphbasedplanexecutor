import networkx as nx
import asyncio

from gpt_api_calls import gpt
from enums import GPT, GPTOutputType
from enums import SystemMessage
    
"""
This class represents a graph that can run an algorithm.
The nodes in this graph are tasks, and the edges are dependencies between the tasks.
So, for example, if we have Task 1 -> Task 2, this means that we execute task 1, then execute task 2 after the completion of task 1.
Notice that this implementation is agnostic of the task type.
To understand how this helps achieve AGI, we need to understand the PlanningTask that we run on this graph.
"""
class AlgorithmGraph:
    # We initiate the graph by providing an edges array between the tasks.
    # The array looks like this: [(Task 1, Task 2), (Task 2, Task 3), ...]
    def __init__(self, edgesArray):
        self.edgesArray = edgesArray
        # TODO: Change startTask to be more programmatic from the graph
        self.startTask = edgesArray[0][0]
        self.graph = nx.DiGraph()
        self.finalResult = None
        self.taskCache = dict()

        self.assignEdgesToGraph()

    # This function takes in the edges we provided to the graph, and uses networkx's graph function to add them to the graph.
    def assignEdgesToGraph(self):
        self.graph.add_edges_from(self.edgesArray)
    
    # This function actually executes the running/stepping through a graph.
    # Provide it with the graph and the task, and it will recursively keep stepping through the graph until the END node is reached for the main graph.
    async def runThroughGraph(self, graph, task):
        if task.humanReadableName == 'END' or task.humanReadableName == 'DONE':
            # task.state.append({task.humanReadableName: 'DONE'})
            task.state.append({task.parentTaskName: 'DONE'})
            print('~~ RETURNING ........')
            return task.state
        
        # Recursively calculate results for successors
        
        # TODO: Allow multiple successors for a node. If the node is a decision/conditional node, some successors will be filtered.
        #successors = []
        #allSuccessors = filter graph.successors(task)
        #for successor in allSuccessors:
        #   edge = graph.edges[task, successor]:
        #   edgeAttributes = edge['attributes']
        #   edgeType = edgeAttributes['type']
        #   if edgeType == 'conditional':
        #       condition = edgeAttributes['condition']
        #       conditionKey = condition.getkeys()[0]
        #       if conditionKey in task.state:
        #           valueFromState = task.state[conditionKey]
        #           valueFromCondition = condition[conditionKey] # This needs to be done using an LLM call
        #           if valueFromState == valueFromCondition:
        #               successors.append(successor)
        #   else:
        #       successors.append(successor)       
        
        # This is a caching mechanism to prevent running the same task with same inputs multiple times.
        # If a task is in the cache, we will use the cached result.
        # If a task is NOT in the cache, we will run the task by calling its "run" method.
        if task.humanReadableName not in self.taskCache:
            await task.run()
        else:
            task.state.append({task.humanReadableName: self.taskCache[task.humanReadableName]})

        # If node is conditional, decide which successor node to run.
        isTaskConditional = task.isConditionalNode

        successors = graph.successors(task)

        # If task is conditional, we will choose successors who match the condition.
        if isTaskConditional is True:
            print(f'~~ Task: {task.humanReadableName} ({task.task}) is conditional')
            formattedStateHistory = task.formatState()
            nextTask = await self.pickNextTask(formattedStateHistory, successors)
            print(f'~~ Picked: {task.humanReadableName}')
            await self.runThroughGraph(nextTask)
        else:
            print(f'~~ Task: {task.humanReadableName} is not conditional. Going to Run Next:')
            for succ in graph.successors(task):
                print(succ.humanReadableName)

            # Then run its successors. No need for successorsResults because each node will add its output to the state
            await asyncio.gather(*[self.runThroughGraph(graph, successor) for successor in graph.successors(task)])


    async def run(self):
        finalResult = await self.runThroughGraph(self.graph, self.startTask)
        self.finalResult = finalResult

        return finalResult
    
    async def pickNextTask(self, stateHistory, successors):
        formattedSuccessors = self.formatSuccessors(successors)
        prompt = f'''Given the following state history (STATE HISTORY) of the steps taken along with their outputs, and the following potential next steps (POTENTIAL NEXT STEPS). Pick the next step whose condition matches the state history (STATE HISTORY):

STATE HISTORY
{stateHistory}

POTENTIAL NEXT STEPS
{formattedSuccessors}

OUTPUT FORMAT (JSON)
Your output MUST be a JSON object that contains the following key:
    "next_task_name": The exact task name of the next task that you pick based on the state history (STATE HISTORY).

'''

        outputJSON, _ = await gpt(GPT.GPT4OMNI, SystemMessage.PLANNER, prompt, outputType=GPTOutputType.JSON)
        pickedNextTaskName = outputJSON['next_task_name']
        nextTask = list(filter(lambda n: n.humanReadableName == pickedNextTaskName, successors))[0]

        return nextTask


    @staticmethod
    def formatSuccessors(successors):
        formattedSuccessorsList =  list(map(lambda successor: f'''Task Name: {successor.humanReadableName} \n Condition: {successor.condition}''', successors))

        return '\n\n'.join(formattedSuccessorsList)
        