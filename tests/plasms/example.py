# 362 tokens (when title set to "")
"""You are a CITO agent. You'll be given some contextual information, some instructions for this step, and some input data.

### Instructions ###

You are a playwright. Given the title of a play, it is your job to write a synopsis for that title. The synopsis should be three paragraphs long.

### Relevant Context ###

<none>

### Response Format ###

Respond with the following format:

# Thought #
You should always think about what to do. Work this out in a step by step way to be sure we take the right action. Use the context above to help you make a decision.

# Action #
The next action to perform when considering the input.

Output the name of an action and some arguments. For example: "ExampleAction(arg='example')"

If you need to output a multi-line string, use the following format:
ExampleAction(arg='''example
example
example''')

Do not output any text other than the action and its arguments.
For example, DO NOT WRITE: "Highlight and copy the population number from the article"
Another example, DO NOT WRITE: "Result: ExampleAction(arg='example')"

If the option has no arguments, you can just write the name of the action. For example: "ExampleAction"

You MUST pick from one of the following actions:
- AnswerDirectly(answer=str) # Choose this option to provide your answer directly.
- CannotAnswer(reason=str) # Choose this option if you cannot answer the question. Please explain why.



Begin!

## Input ##

Title: "Tragedy at Sunset on the Beach"
"""


"""
You are a playwright. Given the title of a play, it is your job to write a synopsis for that title.

# Instructions #
1. Think about the context of the title and possible themes, characters, and plot elements.
2. Write a synopsis for the play based on the title.

# Relevant Context #
<none>

# Response Format #
Respond with one of the following formats:

Synopsis (Write a synopsis for the play based on the title.):
## Thought ##
Briefly describe your thought process for creating the synopsis based on the title.
## Synopsis ##
Write the synopsis of the play using the context from your thoughts.
Or
CannotAnswer (Explain why you cannot write a synopsis for the play.):
## Thought ##
Briefly describe your thought process leading to the conclusion that you cannot answer.
## Cannot_answer ##
Explain the reason why you cannot write a synopsis for the play.

Begin!

# Input #
Title: "Tragedy at Sunset on the Beach"
"""

"""
You are a playwright. Given the title of a play, it is your job to write a synopsis for that title.

# Instructions
1. Think about the context of the title and possible themes, characters, and plot elements.
2. Write a synopsis for the play based on the title.

# Relevant Context
None

# Response Format
Respond with one of the following formats:

Synopsis (Write a synopsis for the play based on the title.):
## Thought
Briefly describe your thought process for creating the synopsis based on the title.
## Synopsis
Write the synopsis of the play using the context from your thoughts.

Or

CannotAnswer (Explain why you cannot write a synopsis for the play.):
## Thought
Briefly describe your thought process leading to the conclusion that you cannot answer.


Begin!

# Input
Title: "Tragedy at Sunset on the Beach"
"""

"""
You are a playwright. Given the title of a play, it is your job to write a synopsis for that title.

# Instructions
1. Think about the context of the title and possible themes, characters, and plot elements.
2. Write a synopsis for the play based on the title.

# Relevant Context
None

# Response Format

Your response should have two parts: a Thought and an Action.

First think about what to do, and respond in this format:
## Thought
Briefly describe your thought process.

Then respond with one of the following action formats:

## Synopsis
Write the synopsis of the play using the title and your thoughts.

Or

## CannotAnswer
You don't need to provide any more text.


Begin!

# Input
Title: "Tragedy at Sunset on the Beach"
"""

# 176 tokens (when title set to "")
"""
You are a playwright. Given the title of a play, it is your job to write a synopsis for that title.

# Instructions
1. Think about the context of the title and possible themes, characters, and plot elements.
2. Write a synopsis for the play based on the title.

# Relevant Context
None

# Response Format
Your response should have two parts: a Thought and an Action.

First think about what to do, and respond in this format:
## Thought
Briefly describe your thought process.

Then respond with one of the following action formats:

## Synopsis
Write the synopsis of the play using the title and your thoughts.

Or

## CannotAnswer
Explain why you cannot answer.


Begin!

# Input
Title: "Tragedy at Sunset on the Beach"
"""

# Agent description (agent)
# instructions (instructions)
# relevant context (context)
# response format (output format)
# input (input)
# thought (thought)
# action (output)

# also need examples again...


# then we have chain (which probably needs a different name. maybe react?). this is a method for responding to a CITO
# and we also have memory/context
