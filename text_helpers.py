import json
import re


def extractJSONSubstring(inputString):
    try:
        asJson = json.loads(inputString)
    except:
        asJson = None

    return asJson

def extractPythonCodeSubstring(inputString):
    # Using regular expression to find Python code substring
    pattern = r'```python(.*?)```'
    match = re.search(pattern, inputString, re.DOTALL)

    if match:
        pythonCodeSubstring = match.group(1).strip()
        return pythonCodeSubstring
    else:
        print("No Python code substring found.")
        return None