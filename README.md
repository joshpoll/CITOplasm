<div align="center" style="display:flex;flex-direction:column;">
  <p>
  <a href="https://discord.gg/ArYxurZU">
    <img alt="CITOplasm logo" src="https://user-images.githubusercontent.com/21694516/232182002-bc1c43ed-6a2e-4278-aade-0c1e215467a1.jpeg" width="10%">
  </a>
  </p>
  <h1>CITOplasm
  <h3>Augment your Python code with flexible LLM functions
  <br />
  like ask, chain, and compare.</h3>
  <p>
    <a href="https://discord.gg/ArYxurZU">
      <img alt="Join our Discord!" src="https://dcbadge.vercel.app/api/server/ArYxurZU?style=flat">
    </a>
  </p>
</div>

## Write Chains
```python
await chain(
  "In what year was the film Departed with Leonardo DiCaprio released? What is this year raised to the 0.43 power?",
  [Search, Python],
)

# The film Departed with Leonardo DiCaprio was released in 2006 and 2006 raised to the 0.43 power is 26.30281917656938.
```

## Add Context
```python
await ask("What is happening on 9/9/2022?")

# I don't know.


await ask(
  "What is happening on 9/9/2022?",
  context="We're running a hackathon on 9/9/2022 to decompose complex reasoning tasks into subtasks that are easier to automate & evaluate with language models....")

# A hackathon is happening on 9/9/2022.
```

## Compare Texts
```python
await info_cmp("A hackathon on 9/9/2022 to decompose complex reasoning tasks into subtasks that are easier to automate & evaluate with language models", "A hackathon is happening on 9/9/2022.")

# MoreInformative()
```

## Built on CITO
`CITO := (context, input) -> (thought, option)`
It's a variation on CQRA (context, question, reasoning, answer) that is more agnostic to inputs and ensures more structured outputs.

```
ask = createCITO("Answer the question as best you can.", [AnswerDirectly, CannotAnswer])
```

# More Info

CITOplasm is a Python library for writing LLM code in a declarative way. Our aim is to eliminate the need to write complicated prompts, templates, and recipes. Instead, we enable people to write compositional programs using base calls to LLMs (CITOs) and normal Python loops, functions, and conditionals.

At the heart of CITOplasm is `createCITO`, a function that creates a CITO prompt. CITO stands for `(context, input) -> (thought, output)`. (It's a variation of CQRA.) On top of base CITO, we have ready-to-use functions that are broadly useful. These currently include `ask`, `chain`, `compare`, and `verify`.

Our future goals include:
- JavaScript/TypeScript support
- more functions
- more robust CITO
- transparent prompt engineering optimizations, perhaps using LMQL
- fleshing out `agent` and `context` concepts

## How to run

To run:
```
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run tests (call from top-level)
```
pytest
```

## How to publish

https://packaging.python.org/en/latest/tutorials/packaging-projects/

## Motivation and Inspiration

This library builds on ICE: https://github.com/oughtinc/ice

Have you ever wondered what it would be like to program with an LLM? Not like use an LLM to produce
traditional code, but to actually program in a language that had LLM primitives? That's what this
repo is exploring.

Currently there are two approaches to this. First, we have very high-level tools like LangChain,
which exposes monolithic chains that are hard to customize. We want to be able to easily create
patterns like debate, amplify, verify, chain-of-thought, etc. from first principles so that we can
explore and optimize these kinds of structures more easily. The second approach is adopted by ICE,
which is to expose a very low-level API of prompt templates. This is expressive enough to get the
job done, but writing string templates is really unstructured and mixes up prompt engineering
concerns (*how* to write your prompt, i.e. prompt engineering) with domain-specific concerns (*what*
to put in your prompt). LangChain also uses prompt templates for extensibility.

Our approach is different. Instead of using prompt templates and recipes, we hide these away beneath
a core set of primitives that abstract over single chat instances with an LLM. Our goal is for
nearly all common LLM+tool patterns that exist today to be representable using a combination of our
primitives and normal Python code without the need for writing prompts or recipes directly. Of
course, we still want it to be possible for end-users to create their own primitives using prompts
and recipes if they want, but we should be able to reduce the need for this.

The primitives we
have so far are:

- **ask** Q&A format
- **chat:** back-and-forth conversations (possibly multiple) with other agents and humans
- **classify** to assign a category to a given input (match)
- **approx-equal and approx-cmp** (uses classify)

Some additional primitives we're thinking about or working on are:

- **decompose** to break apart an input into smaller pieces (destructure)
  - can this be used to implement CoT?
- **enumerate** to list elements of a collection (generator)
- **translate/transform**
- **summarize/reduce**
- **filter/extract/parse/regex**
- **complete**

We are experimenting with whether these primitives can be designed as drop-in replacements for
typical programming constructs. For example, can classify replace match? can approx-equal replace
equal? can summarize replace reduce?

This might give us an easy way to translate rigid programs to flexible, approximate ones. Or even
more precisely, might make it really easy to switch some parts of a program to be rigid and other
parts to be flexible/approximate. It might
help us better organize our primitives and search for missing ones. It might also help us figure out
which LLM interactions present truly novel primitives and which ones are "merely" approximate
versions of existing primitives.

## Observations

Context-Question -> Reasoning-Answer seems to be a robust pattern across Q&A, chat, classify,
equality/comparison. It probably has a name. It's used in the selection-inference paper. CQRA?

Decompose seems to overlap with the reasoning part of Q&A (thinking step by step is a form of decomposition). There are tradeoffs in terms of number of LLM calls (and
maybe that also means tradeoffs in accuracy).

tool selection, multiple choice QA, sub-agent calls can all be built on classify
