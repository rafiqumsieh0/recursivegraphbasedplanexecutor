# Recursive Graph-Based Plan Executor Using LLMs

This project's goal is to build an LLM-based agent that solves problems using long-horizon planning. The implementation of the long-horizon planning is as follows:

1-) Upon receiving a task, the agent initializes a plan as a networkx graph. The nodes in the graph are tasks in the plan, and the edges are execution paths/flows between the nodes. Tasks are reasoning tasks and each task is run using LLM as its reasoning processor.

2-) The graph is parsed programmatically using networkx, and is then executed using Python starting from its initial task.

3-) If a task is complicated (e.g. Type II task: Requires multistep reasoning), it spins up another plan graph to resolve itself. The newly-created graph is executed until it is completed (hence, the "Recursive" in the title). If a task is a simple task (e.g. Type I: Requires a direct inference / direct one-step reasoning), it is executed immediately, and its return value is stored in a "STATE HISTORY" list that stores all previously-taken steps. The "STATE HISTORY" is always passed to the LLM as a form of context.

4-) The program terminates when the main graph's "END" node is reached.

## Table of Contents

- [Current Issues](#current-issues)
- [Contributing](#contributing)
- [Contact](#contact)
- [Installation And Usage](#installation-and-usage)
- [Technologies Used](#technologies-used)
- [License](#license)

## Current Issues

- The main issue right now is: For some problems, the program is stuck in an infinite loop where a new graph keeps getting created, and the main plan never resolves. An example problem is: "Integrate the following integral: e^x*sin(2x)". I am still not sure why this is happening.
- Using a simpler model (GPT 4O Mini) results in somewhat suboptimal reasoning steps, and more infinite loops than intelligent models.
- Using a more intelligent model (GPT 4O) yields more appropriate reasoning steps.

## Contributing

The project needs a lot of work, and any contribution is welcome and appreciated! Your contribution will also be appropriately credited.

## Contact

If you have any questions or need anything, please send me an email at rafi@breakthroughlabs.ai

## Installation And Usage

1. Clone the repository.
2. Go to "playgound.py", and change the "state" and "goal" variables to whatever initial problem you want to solve. Think of the initial state as the problem statement, and the goal as the desired outcome.
3. Run the "playgound.py" file.

## Technologies Used

- **Programming Language**: (Python)
- **Frameworks/Libraries**: (Networkx, OpenAI)

## License

Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

Deed: https://creativecommons.org/licenses/by-nc/4.0/
Legal Code: https://creativecommons.org/licenses/by-nc/4.0/legalcode.en


