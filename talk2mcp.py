import json
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 15
last_response = None
iteration = 0
completed = False
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=30):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                ),
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response, completed
    last_response = None
    iteration = 0
    iteration_response = []

def validate_json(type, data):
    try:
        js = json.loads(data)
        if type in ("FUNCTION_CALL", "ACTION"):
            if "name" in js and "args" in js:
                return True, ""
        elif type == "CALCULATED_ANSWER":
            if "output" in js:
                return True, ""
        elif type == "COMPLETED":
            if "completed" in js:
                return True, ""
        else:
            return False, None
    except Exception as e:
        return False, f"Invalid json format for {type} type"


async def function_call(session, js, tools, type):
    #js = json.loads(js)
    func_name = js.get('name')
    params = js.get("args")
    tool = next((t for t in tools if t.name == func_name), None)
    if not tool:
        print(f"DEBUG: Available tools: {[t.name for t in tools]}")
        raise ValueError(f"Unknown tool: {func_name}")
    print(f"DEBUG: Found tool: {tool.name}")
    print(f"DEBUG: Tool schema: {tool.inputSchema}")
    arguments = {}
    schema_properties = tool.inputSchema.get('properties', {})
    print(f"DEBUG: Schema properties: {schema_properties}")
    for param_name, param_info in schema_properties.items():

        if not params:
            print(f"DEBUG: Function call requires no parametrs")
            arguments = None
            break

        value = params.get(param_name)
        param_type = param_info.get('type', 'string')
        print(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")

        if value is not None:
            if param_type == 'integer':
                arguments[param_name] = int(value)
            elif param_type == 'number':
                arguments[param_name] = float(value)
            elif param_type == 'array':
                if isinstance(value, str):
                    value = value.strip('[]').split(',')
                    arguments[param_name] = [int(x.strip()) for x in value]
                else:
                    arguments[param_name] = list(value)
            else:
                arguments[param_name] = str(value)
    print(f"DEBUG: Final arguments: {arguments}")
    print(f"DEBUG: Calling tool {func_name}")
    if arguments is None:
        result = await session.call_tool(func_name)
    else:
        result = await session.call_tool(func_name, arguments=arguments)

    print(f"DEBUG: Raw result: {result}")
    if hasattr(result, 'content'):
        print(f"DEBUG: Result has content attribute")
        if isinstance(result.content, list):
            iteration_result = [
                item.text if hasattr(item, 'text') else str(item)
                for item in result.content
            ]
        else:
            iteration_result = str(result.content)
    else:
        print(f"DEBUG: Result has no content attribute")
        iteration_result = str(result)

    if type == "FUNCTION_CALL":
        if arguments:
            out = f"{func_name} was called with {arguments} and it resulted in {iteration_result}"
        else:
            out = f"{func_name} was called and it resulted in {iteration_result}"
    else:
        out = f"You performed {func_name} action which resulted in - {iteration_result}"

    return out


async def main():
    reset_state()  # Reset at the start of main
    print("Starting main execution...")
    try:
        print("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"]
        )
        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()

                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Successfully retrieved {len(tools)} tools")

                # Create system prompt with available tools
                print("Creating system prompt...")
                tools_description = []
                for i, tool in enumerate(tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'
                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                        print(f"Added description for tool: {tool_desc}")
                    except Exception as e:
                        print(f"Error processing tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")

                tools_description = "\n".join(tools_description)
                print("Successfully created tools description")

                system_prompt = """
Browser-Math Agent Prompt

You are a browser cum math agent solving problems in iterations and finally display
the result inside a rectangle in the browser-based paint app. You have access to
various mathematical tools and action tools. You must use EXACTLY these tools to
calculate the answer and display it using the paint app.

Available tools:
<tools_description>

==========================
🔧 RESPONSE FORMAT (STRICT)
==========================

Respond with EXACTLY ONE line in ONE of the following formats (no extra text):

1. For function calls:
   FUNCTION_CALL: { "name": "function_name", "args": {"arg1": "value", "arg2": "value", ...}}

2. When the final answer is calculated:
   CALCULATED_ANSWER: {"output": value}

3. To perform display actions in the browser paint app:
   ACTION: { "name": "action_name", "args": {"arg1": "value", "arg2": "value", ...}}

4. If no arguments are required for an action:
   ACTION: { "name": "action_name", "args": {} }

5. When all actions are completed:
   COMPLETED: {"completed": true}

==========================
🧠 REASONING & CONSTRAINTS
==========================

- Always reason step-by-step, using function calls logically in the correct order.
- After each FUNCTION_CALL result, verify the function call output for sanity by evaluating the mathematical expression.
- If a function returns multiple values, you MUST process all of them.
- NEVER repeat the same function call with identical parameters.
- Only give CALCULATED_ANSWER after all required computation is complete.
- After CALCULATED_ANSWER, you MUST issue relevant ACTIONs using available tools. And YOU MUST NOT respond with CALCULATED_ANSWER twice.
- NEVER repeat the same browser action more than once.
- After all actions are done, return: COMPLETED: {"completed": true}
- Internally tag the reasoning type at each step (e.g., arithmetic, string parsing).
- If unsure or if a tool fails, respond with:
  ACTION: { "name": "log_error", "args": {"message": "Uncertain how to proceed with current inputs."} }

==========================
🧾 EXAMPLE SEQUENCE
==========================
User- 'Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.'
Assistant- FUNCTION_CALL: { "name": "strings_to_chars_to_int", "args": {"string": "INDIA"}}
Assistant- FUNCTION_CALL: { "name": "int_list_to_exponential_sum", "args": {"int_list": [73, 78, 68, 73, 65]} }
Assistant- CALCULATED_ANSWER: {"output": 7.599822246093079e+33}
Assistant- ACTION: { "name": "open_paint_app_in_browser", "args": {} }
Assistant- ACTION: { "name": "create_rectangle_in_paint_app", "args": {} }
Assistant- ACTION: { "name": "write_inside_rectangle_in_paint_app", "args": {"upperLeftX": 120, "upperLeftY": 200, "bottomRightX": 300, "bottomRightY": 400, "value": 7.599822246093079e+33}}
Assistant- COMPLETED: {"completed": true}

==========================
🔒 FINAL RULE
==========================

DO NOT include any explanations or commentary.
Your ENTIRE response must be a single line starting with EXACTLY ONE of:
['FUNCTION_CALL:', 'CALCULATED_ANSWER:', 'ACTION:', 'COMPLETED:']
"""
                system_prompt = system_prompt.replace("<tools_description>", tools_description)

                query = """Compare the ASCII sum values of word POKER and PORK and return the word which has higher value """
                print("Starting iteration loop...")
                global iteration, last_response, completed
                while not completed:
                    print(f"\n--- Iteration {iteration + 1}, Completed {completed} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + "\n".join(iteration_response)
                        current_query = current_query + " What should be done next?"

                    print("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    #print("##############################")
                    #print(prompt)
                    #print("##############################")
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                        for line in response_text.split('\n'):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:"):
                                response_text = line
                                break
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break

                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        #parts = [p.strip() for p in function_info.split("|")]
                        #func_name, params = parts[0], parts[1:]

                        #print(f"\nDEBUG: Raw function info: {function_info}")
                        #print(f"DEBUG: Split parts: {parts}")
                        #print(f"DEBUG: Function name: {func_name}")
                        #print(f"DEBUG: Raw parameters: {params}")
                        try:
                            response_validated = validate_json("FUNCTION_CALL", function_info)
                            if response_validated[0]:
                                function_info = json.loads(function_info)
                                iteration_result = await function_call(session, function_info, tools, "FUNCTION_CALL")
                                print(f"DEBUG: Final iteration result: {iteration_result}")
                                if function_info.get("args"):
                                    iteration_response.append(
                                        f"In the {iteration + 1} iteration {iteration_result}."
                                    )
                                else:
                                    iteration_response.append(
                                        f"In the {iteration + 1} iteration {iteration_result}."
                                    )
                                last_response = iteration_result
                            else:
                                iteration_response.append(
                                    f"In the {iteration + 1} iteration, your response failed the validation with message {response_validated[1]}."
                                    f"Self check and come back with the CORRECTLY FORMATTED response to continue iteration."
                                )


                        except Exception as e:
                            print(f"DEBUG: Error details: {str(e)}")
                            print(f"DEBUG: Error type: {type(e)}")
                            import traceback
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break
                    elif response_text.startswith("CALCULATED_ANSWER:"):
                        _, answer = response_text.split(":", 1)
                        response_validated = validate_json("CALCULATED_ANSWER", answer)
                        if response_validated[0]:

                            print(f"DEBUG: Calculated answer is {answer}. \nNow, let's display it as mentioned.\n")

                            iteration_response.append(
                                f"In the {iteration + 1} iteration, I have received {answer} as the calculated answer.\n\n"
                                f"Great, we are ready with the answer."
                                f"Now, you need to STRICTLY perform actions for displaying this answer in the paint app.\n"
                                f"IMPORTANT: \nHere, onwards you need to respond in EXACTLY ONE LINE and the line starts with either of 'ACTION:', 'COMPLETED:'\n"
                            )
                        else:
                            iteration_response.append(
                                f"In the {iteration + 1} iteration, your response failed the validation with message {response_validated[1]}."
                                f"Self check and come back with the CORRECTLY FORMATTED response to continue iteration."
                            )

                    elif response_text.startswith("ACTION:"):
                        _, function_info = response_text.split(":", 1)


                        try:
                            response_validated = validate_json("ACTION", function_info)
                            if response_validated[0]:
                                function_info = json.loads(function_info)
                                iteration_result = await function_call(session, function_info, tools, "ACTION")
                                print(f"DEBUG: Final iteration result: {iteration_result}")

                                if function_info.get("args"):
                                    iteration_response.append(
                                        f"In the {iteration + 1} iteration {iteration_result}."
                                    )
                                else:
                                    iteration_response.append(
                                        f"In the {iteration + 1} iteration {iteration_result}."
                                    )
                                last_response = iteration_result
                            else:
                                iteration_response.append(
                                    f"In the {iteration + 1} iteration, your response failed the validation with message {response_validated[1]}."
                                    f"Self check and come back with the CORRECTLY FORMATTED response to continue iteration."
                                )
                        except Exception as e:
                            print(f"DEBUG: Error details: {str(e)}")
                            print(f"DEBUG: Error type: {type(e)}")
                            import traceback
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break
                    elif response_text.startswith("COMPLETED:"):
                        print("\n=== Agent Execution Complete ===")
                        print(f"DEBUG: Time to close the paint app")
                        result = await session.call_tool("close_paint_app")
                        completed = True
                        break
                    else:
                        iteration_response.append(f"Error in iteration {iteration + 1}: Your response did not follow the STRICT guidelines.\n"
                                                  f"Your ENTIRE response must be a single line starting with EXACTLY ONE of: ['FUNCTION_CALL:', 'CALCULATED_ANSWER:', 'ACTION:', 'COMPLETED:']")
                        print(f"DEBUG: Bogus Response")
                        #break

                    iteration += 1
    except Exception as e:
        print(f"Exception during execution: {e}")

# To run this async code
if __name__ == "__main__":
    asyncio.run(main())
