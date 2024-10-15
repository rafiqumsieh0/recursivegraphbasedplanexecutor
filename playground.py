import asyncio

from tasks import PlanningTask
from enums import SystemMessage

"""
We start any algorithm here with the start method. The start method requires the following:
- state: A current state to give context to the agent of what state it is in. This is very dependant on the task.
- goal: The ultimate goal that the agent needs to achieve for this algorithm.

The function takes the state & goal, and produces a plan using a PlanningTask.
It, then, runs the PlanningTask using its "run" method.

A plan in this case is a graph of tasks that the agent needs to follow to reach its goal.
"""
async def start(): 

    # The state is the INPUT to the system
    state = [{f'''You face the following problem: The planet Pluto (radius 1180 km) is populated by three species of purple
caterpillar. Studies have established the following facts:
 A line of 5 mauve caterpillars is as long as a line of 7 violet caterpil-
lars.
 A line of 3 lavender caterpillars and 1 mauve caterpillar is as long as
a line of 8 violet caterpillars.
 A line of 5 lavender caterpillars, 5 mauve caterpillars and 2 violet
caterpillars is 1 m long in total.
 A lavender caterpillar takes 10 s to crawl the length of a violet cater-
pillar.
 Violet and mauve caterpillars both crawl twice as fast as lavender
caterpillars.
How long would it take a mauve caterpillar to crawl around the equator
of Pluto?''': 'RUNNING'}]
    
    # The  goal is the preferred OUTPUT of the system
    goal = 'Solve the problem correctly.'
    
    rulesList = []
    expectedOutputJSONSchema = ['output']
    description = ''
    reasoningType = ''
    parentTaskName = None
    inputTuple = (rulesList, state, goal, expectedOutputJSONSchema, description, reasoningType, parentTaskName)
    humanReadableTaskName = 'CREATE MAIN PLAN ALGORITHM GRAPH'
    systemMessage = SystemMessage.PLANNER

    mainPlanTask = PlanningTask(humanReadableTaskName, systemMessage, inputTuple)
    await mainPlanTask.run()

if __name__ == '__main__':

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no running loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # loop = asyncio.get_event_loop()
    res = loop.run_until_complete(start())
    print(res)
    loop.close()