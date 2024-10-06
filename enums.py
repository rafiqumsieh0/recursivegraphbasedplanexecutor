from enum import Enum

class GPT(Enum):
    GPT4OMNI = 'gpt-4o'
    GPT4OMNIMINI = 'gpt-4o-mini'

class GPTOutputType(Enum):
    TEXT = 'TEXT'
    JSON = 'JSON'
    CODE = 'CODE'

class SystemMessage(Enum):
    PLANNER = 'You are an expert on the following topics: Planning, Algorithms, Diagrams, Logic, Problem Solving, High-Level Thinking.'
    EMPTY = ''