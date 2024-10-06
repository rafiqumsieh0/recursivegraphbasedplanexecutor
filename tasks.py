import json

from gpt_api_calls import gpt
from enums import GPT, GPTOutputType
from graph import AlgorithmGraph

"""
This class represents a planning task. A planning task is a task that creates a plan.
The plan in this case is a graph where the nodes are tasks in the plan, and the edges are dependencies among these tasks.
The way the Planning Task works is the following:
1-) It takes a state history, goal, and task in as inputs.
2-) It reasons about them using an LLM.
- If the response from the LLM indicates the reaching of the final goal, it stores the final results and terminates.
- Else if the response from the LLM does not indicate reaching the final goal, it spins up another plan (algorithmic graph) and runs it.
3-) It keeps doing this recursively until the final goal is reached.
"""
class PlanningTask:
    def __init__(self, humanReadableName, systemMessage, inputTuple, isConditionalNode=False):

        rulesList, state, goal, expectedOutputJSONSchema, description, reasoningType, parentTaskName = inputTuple

        self.humanReadableName = humanReadableName
        self.systemMessage = systemMessage
        self.isConditionalNode = isConditionalNode
        self.rulesList = rulesList
        self.state = state
        self.goal = goal
        self.expectedOutputJSONSchema = expectedOutputJSONSchema
        self.description = description
        self.reasoningType = reasoningType
        self.parentTaskName = parentTaskName
        self.condition = None
        self.rules = None
        self.outputJSON = None
        self.task = self.determineTask()
    
    @staticmethod
    def convertinputDataDictsToSingleJSON(inputDataDicts):
        finalDict = {}

        for inputDict in inputDataDicts:
            # Convert JSON to Dict
            inputDictAsJSON = json.loads(inputDict)
            finalDict.update(inputDictAsJSON)
        
        # Convert final output from Dict to JSON
        finalInputJSON = json.dumps(finalDict)

        return finalInputJSON


    def determineTask(self):
        reasoningType = self.reasoningType
        if reasoningType is None or reasoningType == '':
            return f'''You must choose ONE from the following:

Option 1: Evaluate if you can directly satisfy the goal (GOAL) by reviewing the provided state history (STATE HISTORY) above. If you can achieve this without additional computations, you MUST return a pure JSON object that contains the following key/value pair: key is: “answer” and its value is: the actual answer that you found from the state. It cannot be ambigious, and it cannot be another task. It must be a clear returned value.
Option 2: If the state history (STATE HISTORY) does not provide sufficient information to directly satisfy the goal (GOAL), create a Python networkx graph represented in JSON format to outline the algorithm or plan you will use to achieve the goal, given the current state history (STATE HISTORY). The graph MUST be a JSON object that contains the following keys:
    "nodes": This must contain all the graph's nodes in the networkx graph. The nodes will represent subtasks that you will take. Each node will be a JSON object that contains "id" key. The "id" should be a human-readable short description of the node. Each node MUST also contain a "description" key that describes the node's function in more details than the "id". A maximum of one sentence is allowed. Each node must include its reasoning type "type" (type I for direct computation tasks vs. type II for more multi-step computations). If a node is a conditional node, you should add the key "conditional" to it. The graph MUST NOT contain a "START" node. The graph MUST contain an "END" node to represent the termination node of the algorithm.
    "edges": This must contain all the graph's edges. If an edge is a conditional edge, you should add the key "condition" that specifies the condition as a string. Each edge is an object that contains a "source" and a "target" node ids. The ids should match the node ids you define.
'''
        elif reasoningType == 'type I':
            return 'Use the provided state history (STATE HISTORY) to achieve the goal (GOAL). You MUST return a pure JSON object that contains the following key/value pair: key is: “answer” and its value is: the actual answer that you found from the state. It cannot be ambigious, and it cannot be another task. It must be a clear computed returned value.'
        
        elif reasoningType == 'type II':
            return '''If the state history (STATE HISTORY) does not provide sufficient information to directly satisfy the goal (GOAL), create a Python networkx graph represented in JSON format to outline the algorithm or plan you will use to achieve the goal, given the current state history (STATE HISTORY). The graph MUST be a JSON object that contains the following keys:
    "nodes": This must contain all the graph's nodes in the networkx graph. The nodes will represent subtasks that you will take. Each node will be a JSON object that contains "id" key. The "id" should be a human-readable short description of the node. Each node MUST also contain a "description" key that describes the node's function in more details than the "id". A maximum of one sentence is allowed. Each node must include its reasoning type "type" (type I for direct computation tasks vs. type II for more multi-step computations). If a node is a conditional node, you should add the key "conditional" to it. The graph MUST NOT contain a "START" node. The graph MUST contain an "END" node to represent the termination node of the algorithm.
    "edges": This must contain all the graph's edges. If an edge is a conditional edge, you should add the key "condition" that specifies the condition as a string. Each edge is an object that contains a "source" and a "target" node ids. The ids should match the node ids you define.
'''

    def assembleRules(self):
        rulesString = ''
        newLine = '\n'

        for index, rule in enumerate(self.rulesList):
            rulesString += f'- {rule}{newLine}'
        self.rules = rulesString

        return rulesString
    
    def formatState(self):

        formattedStateList = []
        for stateIndex, state in enumerate(self.state):
            for key, value in state.items():
                formattedStateList.append(f'''Step #{stateIndex}:\n\tId: {key}\n\tReturn Value: {value}''')

        return '\n'.join(formattedStateList)

    def assemblePrompt(self):
        formattedState = self.formatState()
        prompt = f'''You will be presented with the following:

- State History (STATE HISTORY): This is a list of all previously taken steps along with their returned values.
- Goal (GOAL): A goal you MUST achieve.
- Goal Description (GOAL DESCRIPTION): A more detailed description of the goal (GOAL).
- Task (TASK): A task to perform given the full state history (STATE HISTORY) and the goal (GOAL).

Here is the information:

STATE HISTORY
{formattedState}

GOAL
{self.goal}

GOAL DESCRIPTION
{self.description}

TASK
{self.task}
If you end up creating a graph (Option 2), avoid creating nodes from the state history (STATE HISTORY). The nodes cannot contain the following node: {self.goal}
'''
        
        return prompt
    

    async def run(self, inputJSONs=None):
        if inputJSONs:
            self.inputJSON = self.convertinputDataDictsToSingleJSON(inputJSONs)
        
        self.rules = self.assembleRules()
        self.prompt = self.assemblePrompt()

        print('DETAILED STATE HISTORY:')
        for state in self.state:
            for key, value in state.items():
                print(f'{key}: {value}')
        print('-------------------------')
            
        # print(self.prompt)
        """ DIRECTLY USING OPENAI """
        outputJSON, _ = await gpt(GPT.GPT4OMNI, self.systemMessage, self.prompt, outputType=GPTOutputType.JSON)

        print('GPT OUTPUT:')
        print(outputJSON)
        # print('-------------------------')
        self.outputJSON = outputJSON

        await self.evaluateLLMResponse()

    # This function evaluates the JSON response from the reasoning LLM.
    # If the JSON response contains the key "answer", this means we have reached the goal and got an answer, so terminate.
    # If the JSON response does not contain the key "answer", this means that we need to create the next plan.
    async def evaluateLLMResponse(self):
        # outputAsDict = json.loads(self.outputJSON)
        outputJSON = self.outputJSON

        if 'answer' in outputJSON.keys():
            # for state in self.state:
            #     for key, value in state:
            #         if key == self.parentTaskName:
            #             state[key].append({self.humanReadableName: outputJSON['answer']})
            self.state.append({self.humanReadableName: outputJSON['answer']})
        else:
            print(f'~~ Going to spin off a new graph for task: {self.humanReadableName}')
            await self.createAndRunGraphForTask()


    # This function, as the name suggests, creates and runs a plan.
    # It takes in the response from the LLM. The response contains a plan in the form of nodes and edges.
    # The nodes are tasks, and the edges are dependencies.
    # It then creates a networkx Algorithmic Graph representing the plan, and executes it.
    async def createAndRunGraphForTask(self):
        graph = self.outputJSON
        # graph = json.loads(graphJSONDescription)

        nodes = graph['nodes']
        edges = graph['edges']

        finalNodes = []
        finalEdges = []
        
        self.state.append({self.goal: 'RUNNING'})

        for _, node in enumerate(nodes):
            task = self.task
            rulesList = []
            state = self.state
                
            goal = node['id']
            description = node['description']
            reasoningType = node['type']
            expectedOutputJSONSchema = ['output']

            humanReadableName = node['id']
            systemMessage = self.systemMessage
            parentTaskName = self.humanReadableName

            inputTuple = rulesList, state, goal, expectedOutputJSONSchema, description, reasoningType, parentTaskName

            if 'conditional' in node:
                isConditionalNode = True
            else:
                isConditionalNode = False
            
            task = PlanningTask(humanReadableName, systemMessage, inputTuple, isConditionalNode)

            finalNodes.append(task)

        for edge in edges:
            sourceID = edge['source']
            targetID = edge['target']
 
            sourceTask = list(filter(lambda n: n.humanReadableName == sourceID, finalNodes))[0]
            targetTask = list(filter(lambda n: n.humanReadableName == targetID, finalNodes))[0]
            if 'condition' in edge:
                targetTask.condition = edge['condition']

            # finalEdges.append((sourceTask, targetTask, isConditionalEdge))
            finalEdges.append((sourceTask, targetTask))

        algorithmGraph = AlgorithmGraph(finalEdges)
        
        finalResult = await algorithmGraph.run()

        print(finalResult)