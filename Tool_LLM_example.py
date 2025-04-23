import google.generativeai as genai
import requests

# Substitute your API key here
genai.configure(api_key="AIzaSyBVAnfJ2pBNIliT7N2evGM16c7SZwtiUio")

# Weather API
def get_weather(city: str) -> str:
    url = "https://wttr.in/{}?format=3".format(city)
    response = requests.get(url)
    return response.text

# Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Get the weather for a given city",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "Chicago"}
            },
            "required": ["city"]
        }
    }
]

# Create model + tool
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-pro-exp-03-25",
    tools=tools,
)

# User interaction
chat = model.start_chat()

response = chat.send_message(
    "Help me get the weather for Chicago today",
    tool_config={"function_calling_config": {"mode": "AUTO"}}
)

# Check if the tool is called
if (response.candidates and
    response.candidates[0].content and
    response.candidates[0].content.parts and
    response.candidates[0].content.parts[0].function_call):

    tool_call = response.candidates[0].content.parts[0].function_call
    print(f"Gemini decides to use tool: {tool_call.name}({tool_call.args})")

    # Actual tool call
    if 'city' in tool_call.args:
        result = get_weather(tool_call.args['city'])

        # Construct the function response as a dictionary
        function_response_payload = {
            "function_response": {
                "name": tool_call.name,
                "response": {
                    "content": result,
                }
            }
        }

        followup = chat.send_message(
            content=function_response_payload
        )

        print("Gemini answer:", followup.text)
    else:
        print("Error: 'city' argument not found in tool call arguments.")
else:
    # Handle cases where Gemini responds directly or an error occurs
    try:
        print("Gemini direct answer (or error):", response.text)
    except ValueError:
         print("Gemini response did not contain text. Full response:", response)