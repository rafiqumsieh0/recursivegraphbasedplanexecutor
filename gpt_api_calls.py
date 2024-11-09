import os

from openai import OpenAI

from enums import GPTOutputType
from text_helpers import extractJSONSubstring, extractPythonCodeSubstring

openAIAPIKey = os.environ['OPENAI_KEY_SECRET']
client = OpenAI(api_key=openAIAPIKey) 


async def gpt(modelName, systemMessage, prompt, outputType):

    if outputType == GPTOutputType.TEXT:
        response = client.chat.completions.create(
        messages=[
            {
                "role": 'system',
                "content": systemMessage.value
            },
                            {
                "role": 'user',
                "content": prompt,
            }
        ],
        model=modelName.value,
        temperature=1.0,
        )
        outputJSON = response.choices[0].message.content

        return (outputJSON, None)

    elif outputType == GPTOutputType.JSON:

        response = client.chat.completions.create(
        messages=[
            {
                "role": 'system',
                "content": systemMessage.value
            },
                            {
                "role": 'user',
                "content": prompt,
            }
        ],
        response_format={ "type": "json_object" },
        model=modelName.value,
        temperature=0.0,
        )

        outputJSON = response.choices[0].message.content
        outputJSON = extractJSONSubstring(outputJSON)

        return (outputJSON, None)

    elif outputType == GPTOutputType.CODE:

        response = client.chat.completions.create(
        messages=[
            {
                "role": 'system',
                "content": systemMessage.value
            },
                            {
                "role": 'user',
                "content": prompt,
            }
        ],
        model=modelName.value,
        )
        fullResponse = response.choices[0].message.content
        outputJSON = extractPythonCodeSubstring(fullResponse)

        return (outputJSON, fullResponse)