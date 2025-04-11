# **S5EAGv1**

## **📌 Problem Statement**
A Simple MCP Server based AI Mathematical Agent which follows CoT (Chain of Thoughts) Reasoning / ReAct to execute calculation based query. Once the answer is generated, it opens
browser based Paint App and displays the result inside a rectangle. Here is the [video](https://youtu.be/rgBqDNkDyYA)

#### **System Prompt**

```
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
```
#### ** Prompt Validation by ChatGPT **

```
{
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": true,
  "fallbacks": true,
  "overall_clarity": "Excellent structure with strong guidance for tool use, reasoning flow, and response formatting. Now fully supports internal self-checks, reasoning tagging, and fallback instructions, making it highly robust for structured, iterative reasoning tasks."
}

```

#### **Agent Execution Logs**
```
Starting main execution...
Establishing connection to MCP server...
Connection established, creating session...
Session created, initializing...
Requesting tool list...
[04/11/25 23:41:42] INFO     Processing request of type ListToolsRequest                                                                                                                       server.py:534
Successfully retrieved 25 tools
Creating system prompt...
Added description for tool: 1. add(a: integer, b: integer) - Add two numbers. The equivalent mathematical expression is : (a + b)
Added description for tool: 2. add_list(l: array) - Add all numbers in a list. The equivalent mathematical expression is: l[0] + l[1] + ...
Added description for tool: 3. subtract(a: integer, b: integer) - Subtract two numbers. The equivalent mathematical expression is : (a - b)
Added description for tool: 4. multiply(a: integer, b: integer) - Multiply two numbers. The equivalent mathematical expression is : (a * b)
Added description for tool: 5. divide(a: integer, b: integer) - Divide two numbers. The equivalent mathematical expression is : (a / b)
Added description for tool: 6. power(a: integer, b: integer) - Power of two numbers. The equivalent mathematical expression is : (a ** b)
Added description for tool: 7. sqrt(a: integer) - Square root of a number. The equivalent mathematical expression is : (a ** 0.5)
Added description for tool: 8. cbrt(a: integer) - Cube root of a number. The equivalent mathematical expression is : (a ** (1/3))
Added description for tool: 9. factorial(a: integer) - factorial of a number. The equivalent mathematical expression is : int(math.factorial(a))
Added description for tool: 10. log(a: integer) - log of a number. The equivalent mathematical expression is : float(math.log(a))
Added description for tool: 11. remainder(a: integer, b: integer) - remainder of two numbers division. The equivalent mathematical expression is : int(a % b)
Added description for tool: 12. sin(a: integer) - sin of a number. The equivalent mathematical expression is : float(math.sin(a))
Added description for tool: 13. cos(a: integer) - cos of a number. The equivalent mathematical expression is : float(math.cos(a))
Added description for tool: 14. tan(a: integer) - tan of a number. The equivalent mathematical expression is : float(math.tan(a))
Added description for tool: 15. mine(a: integer, b: integer) - special mining tool. The equivalent mathematical expression is : int(a - b - b)
Added description for tool: 16. create_thumbnail(image_path: string) - Create a thumbnail from an image
Added description for tool: 17. strings_to_chars_to_int(string: string) - Return the ASCII values of the characters in a word
Added description for tool: 18. int_list_to_exponential_sum(int_list: array) - Return sum of exponentials of numbers in a list
Added description for tool: 19. fibonacci_numbers(n: integer) - Return the first n Fibonacci Numbers
Added description for tool: 20. compare(a: number, b: number) - Return 1 if a is greater than b otherwise -1 in case b is less than a. It returns 0 if a equals to b.
Added description for tool: 21. evaluate(expression: string) - Calculate the mathematical expression given in the input.
Added description for tool: 22. open_paint_app_in_browser() - This ACTION opens paint app in browser which can be used to draw any shapes eg rectangle, circle, ellipse etc.
    It can also be used to write text. 
Added description for tool: 23. create_rectangle_in_paint_app() - This ACTION creates a rectangle in the paint app if the paint app is open. If paint app is not open, the rectangle is not created.
    Make sure the paint app is open before making this action call.
    By default, the upper left corner of the rectangle is at position (150, 300) and lower right corer of the rectangle is at (400, 500).
    
Added description for tool: 24. write_inside_rectangle_in_paint_app(upperLeftX: integer, upperLeftY: integer, bottomRightX: integer, bottomRightY: string, value: string) - This ACTION writes value inside the rectangle with upper left position (upperLeftX, upperLeftY)
    and bottom right position (bottomRightX, bottomRightY).
    Make sure the paint app is open. In case the paint app is not open, it fails to write the text.

    
Added description for tool: 25. close_paint_app() - 
Successfully created tools description
Starting iteration loop...

--- Iteration 1, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: { "name": "strings_to_chars_to_int", "args": {"string": "POKER"}}
DEBUG: Found tool: strings_to_chars_to_int
DEBUG: Tool schema: {'properties': {'string': {'title': 'String', 'type': 'string'}}, 'required': ['string'], 'title': 'strings_to_chars_to_intArguments', 'type': 'object'}
DEBUG: Schema properties: {'string': {'title': 'String', 'type': 'string'}}
DEBUG: Converting parameter string with value POKER to type string
DEBUG: Final arguments: {'string': 'POKER'}
DEBUG: Calling tool strings_to_chars_to_int
[04/11/25 23:41:45] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='80', annotations=None), TextContent(type='text', text='79', annotations=None), TextContent(type='text', text='75', annotations=None), TextContent(type='text', text='69', annotations=None), TextContent(type='text', text='82', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: strings_to_chars_to_int was called with {'string': 'POKER'} and it resulted in ['80', '79', '75', '69', '82']

--- Iteration 2, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: { "name": "strings_to_chars_to_int", "args": {"string": "PORK"}}
DEBUG: Found tool: strings_to_chars_to_int
DEBUG: Tool schema: {'properties': {'string': {'title': 'String', 'type': 'string'}}, 'required': ['string'], 'title': 'strings_to_chars_to_intArguments', 'type': 'object'}
DEBUG: Schema properties: {'string': {'title': 'String', 'type': 'string'}}
DEBUG: Converting parameter string with value PORK to type string
DEBUG: Final arguments: {'string': 'PORK'}
DEBUG: Calling tool strings_to_chars_to_int
                    INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='80', annotations=None), TextContent(type='text', text='79', annotations=None), TextContent(type='text', text='82', annotations=None), TextContent(type='text', text='75', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: strings_to_chars_to_int was called with {'string': 'PORK'} and it resulted in ['80', '79', '82', '75']

--- Iteration 3, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: { "name": "add_list", "args": {"l": [80, 79, 75, 69, 82]} }
DEBUG: Found tool: add_list
DEBUG: Tool schema: {'properties': {'l': {'items': {}, 'title': 'L', 'type': 'array'}}, 'required': ['l'], 'title': 'add_listArguments', 'type': 'object'}
DEBUG: Schema properties: {'l': {'items': {}, 'title': 'L', 'type': 'array'}}
DEBUG: Converting parameter l with value [80, 79, 75, 69, 82] to type array
DEBUG: Final arguments: {'l': [80, 79, 75, 69, 82]}
DEBUG: Calling tool add_list
[04/11/25 23:41:47] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='385', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: add_list was called with {'l': [80, 79, 75, 69, 82]} and it resulted in ['385']

--- Iteration 4, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: { "name": "add_list", "args": {"l": [80, 79, 82, 75]} }
DEBUG: Found tool: add_list
DEBUG: Tool schema: {'properties': {'l': {'items': {}, 'title': 'L', 'type': 'array'}}, 'required': ['l'], 'title': 'add_listArguments', 'type': 'object'}
DEBUG: Schema properties: {'l': {'items': {}, 'title': 'L', 'type': 'array'}}
DEBUG: Converting parameter l with value [80, 79, 82, 75] to type array
DEBUG: Final arguments: {'l': [80, 79, 82, 75]}
DEBUG: Calling tool add_list
[04/11/25 23:41:48] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='316', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: add_list was called with {'l': [80, 79, 82, 75]} and it resulted in ['316']

--- Iteration 5, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: { "name": "compare", "args": {"a": 385, "b": 316}}
DEBUG: Found tool: compare
DEBUG: Tool schema: {'properties': {'a': {'title': 'A', 'type': 'number'}, 'b': {'title': 'B', 'type': 'number'}}, 'required': ['a', 'b'], 'title': 'compareArguments', 'type': 'object'}
DEBUG: Schema properties: {'a': {'title': 'A', 'type': 'number'}, 'b': {'title': 'B', 'type': 'number'}}
DEBUG: Converting parameter a with value 385 to type number
DEBUG: Converting parameter b with value 316 to type number
DEBUG: Final arguments: {'a': 385.0, 'b': 316.0}
DEBUG: Calling tool compare
[04/11/25 23:41:49] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='1', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: compare was called with {'a': 385.0, 'b': 316.0} and it resulted in ['1']

--- Iteration 6, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: CALCULATED_ANSWER: {"output": "POKER"}
DEBUG: Calculated answer is  {"output": "POKER"}. 
Now, let's display it as mentioned.


--- Iteration 7, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: ACTION: { "name": "open_paint_app_in_browser", "args": {} }
DEBUG: Found tool: open_paint_app_in_browser
DEBUG: Tool schema: {'properties': {}, 'title': 'open_paint_app_in_browserArguments', 'type': 'object'}
DEBUG: Schema properties: {}
DEBUG: Final arguments: {}
DEBUG: Calling tool open_paint_app_in_browser
[04/11/25 23:41:51] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='The browser is open now. Now trying to open the paint app.\nThe paint app was successfully opened in the browser as well.', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: You performed open_paint_app_in_browser action which resulted in - ['The browser is open now. Now trying to open the paint app.\nThe paint app was successfully opened in the browser as well.']

--- Iteration 8, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: ACTION: { "name": "create_rectangle_in_paint_app", "args": {} }
DEBUG: Found tool: create_rectangle_in_paint_app
DEBUG: Tool schema: {'properties': {}, 'title': 'create_rectangle_in_paint_appArguments', 'type': 'object'}
DEBUG: Schema properties: {}
DEBUG: Final arguments: {}
DEBUG: Calling tool create_rectangle_in_paint_app
[04/11/25 23:42:08] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='The rectangle with upper left corner (x: 150, y: 300) and bottom right corner (x: 400, y: 500) is created successfully.', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: You performed create_rectangle_in_paint_app action which resulted in - ['The rectangle with upper left corner (x: 150, y: 300) and bottom right corner (x: 400, y: 500) is created successfully.']

--- Iteration 9, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: ACTION: { "name": "write_inside_rectangle_in_paint_app", "args": {"upperLeftX": 160, "upperLeftY": 320, "bottomRightX": 380, "bottomRightY": 480, "value": "POKER"}}
DEBUG: Found tool: write_inside_rectangle_in_paint_app
DEBUG: Tool schema: {'properties': {'upperLeftX': {'title': 'Upperleftx', 'type': 'integer'}, 'upperLeftY': {'title': 'Upperlefty', 'type': 'integer'}, 'bottomRightX': {'title': 'Bottomrightx', 'type': 'integer'}, 'bottomRightY': {'title': 'bottomRightY', 'type': 'string'}, 'value': {'title': 'Value', 'type': 'string'}}, 'required': ['upperLeftX', 'upperLeftY', 'bottomRightX', 'bottomRightY', 'value'], 'title': 'write_inside_rectangle_in_paint_appArguments', 'type': 'object'}
DEBUG: Schema properties: {'upperLeftX': {'title': 'Upperleftx', 'type': 'integer'}, 'upperLeftY': {'title': 'Upperlefty', 'type': 'integer'}, 'bottomRightX': {'title': 'Bottomrightx', 'type': 'integer'}, 'bottomRightY': {'title': 'bottomRightY', 'type': 'string'}, 'value': {'title': 'Value', 'type': 'string'}}
DEBUG: Converting parameter upperLeftX with value 160 to type integer
DEBUG: Converting parameter upperLeftY with value 320 to type integer
DEBUG: Converting parameter bottomRightX with value 380 to type integer
DEBUG: Converting parameter bottomRightY with value 480 to type string
DEBUG: Converting parameter value with value POKER to type string
DEBUG: Final arguments: {'upperLeftX': 160, 'upperLeftY': 320, 'bottomRightX': 380, 'bottomRightY': '480', 'value': 'POKER'}
DEBUG: Calling tool write_inside_rectangle_in_paint_app
[04/11/25 23:42:12] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:534
DEBUG: Raw result: meta=None content=[TextContent(type='text', text='the POKER is written inside the text box with upper left position at (x: 160, y: 320) and bottom left position at (x: 380, y: 480) successfully', annotations=None)] isError=False
DEBUG: Result has content attribute
DEBUG: Final iteration result: You performed write_inside_rectangle_in_paint_app action which resulted in - ['the POKER is written inside the text box with upper left position at (x: 160, y: 320) and bottom left position at (x: 380, y: 480) successfully']

--- Iteration 10, Completed False ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: COMPLETED: {"completed": true}

=== Agent Execution Complete ===
DEBUG: Time to close the paint app
```

#### **To Execute, simply run the following command**
```
python talk2mcp.py 
```
