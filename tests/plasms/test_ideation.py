from typing import List, Tuple
import pytest
from citoplasm.functions import distill
from citoplasm.functions.ask import ask

from citoplasm.functions.generate import CannotAnswer, ItemList, generate

from ice.utils import map_async


async_map = map_async


# TODO: I really want to be able to ask a follow-up question...
async def why_pain_point(
    pain_point: str,
) -> str:
    return await ask(
        "Consider the pain point in the context. Why is it important, and why is it difficult to achieve?",
        context=f"""
                ## Pain Point
                {pain_point}
                """,
    )


@pytest.mark.asyncio
async def test_ideation_jupyter_notebook_research():
    pain_points = await generate(
        "5",
        "high impact pain points for Jupyter notebook users. A pain point has high impact if it is both an important task and also difficult to achieve. It should also be a pain point that is unique to Jupyter notebooks and doesn't apply to regular programming in text files. An example of a high impact pain point is setup: Loading and cleaning data from multiple sources and platforms is a tortuous, multi-step, manual process.",
    )
    print(pain_points)
    print()

    assert isinstance(pain_points, ItemList)

    why_pain_points = await async_map(
        pain_points.items,
        why_pain_point,
    )

    print(why_pain_points)
    print()

    # not useful here...
    # distilled_root_causes = await distill(why_pain_points)
    # print(distilled_root_causes)

    design_principles = await generate(
        "3-5",
        "principles of programming languages design. An example of a principle of programming languages design is simplicity: The language should be simple to learn and use.",
    )

    print(design_principles)
    # for each pain point, explore why that pain point exists. what is the root cause?
    # after you've identified root causes, see if you can anti-unify them into a single root cause (e.g. "data is messy")
    # for each distilled root cause, explore what are the possible solutions to that root cause

    potential_solutions = await async_map(
        list(zip(pain_points.items, why_pain_points)),
        address_pain_point,
    )

    print(potential_solutions)

    distilled_solution = await distill(potential_solutions)
    print(distilled_solution)


async def address_pain_point(
    pain_point_and_design_principles: Tuple[str, List[str]]
) -> str:
    pain_point, design_principles = pain_point_and_design_principles
    return await ask(
        "You are a Programming Languages researcher. Consider the pain point and programming languages design principles in the context. What are some ideas for how we can apply these design principles to address the pain point? Be specific and concrete.",
        context=f"""
                ## Pain Point
                {pain_point}
                ## Programming Languages Design Principles
                {design_principles}
                """,
        debug=True,
    )


async def explore_root_cause(
    pain_point_and_design_principles: Tuple[str, List[str]]
) -> str:
    pain_point, design_principles = pain_point_and_design_principles
    return await ask(
        "You are a Programming Languages researcher. Consider the pain point and programming languages design principles in the context. What might be the root cause of this pain point? Be specific and concrete.",
        context=f"""
                ## Pain Point
                {pain_point}
                ## Programming Languages Design Principles
                {design_principles}
                """,
        debug=True,
    )


@pytest.mark.asyncio
async def test_ideation_jupyter_notebook_research_user_directed():
    # From Chattopadhyay et al. 2020
    # TODO: it may make sense to include existing solutions in addition to these pain points and critique those solutions using principles of programming languages design. this could help guide us to better solutions.
    pain_points = {
        "Refactor code": """When compared with traditional integrated development environments, such as Visual Studio Code or PyCharm, our data scientists report that proper coding assistance within notebooks is almost non-existent. Familiar features like autocompletion, refactoring tools, and live templates are often missing or do not function properly. Consequently, data scientists spend substantial time using online resources like Stack Overflow or documentation to help them code. Even when code snippets were available online, data scientists had to manipulate and wrangle these snippets to fit within their existing code, introducing unnecessary clerical errors in the process.
In many ways, coding assistance is possibly even more important to data scientists than software engineers: for data scientists, coding is primarily a means to answer questions about their data, and not the core activity of interest. Languages such as R and Python are popular with data scientists because of their "swiss-army knife" capabilities, but the flexibility of these languages—for example, dynamic typing and reflection—make them difficult for static analysis tools to reason about. For researchers, it's important that we support the languages data scientists actually use, not the languages we wish they would use.""",
        "Deploy into production": """Deploying and adapting exploratory notebooks for production environments, such as customer-facing applications, requires data scientists to acquire expertise in a skill set that is well outside of their core, day-to-day responsibilities. While larger organizations have data engineering or software engineering teams to assist data scientists in deployment, in smaller organizations data scientists must take on these responsibilities themselves. There are several opportunities to improve the data scientists' user experience and productivity. First, the programming languages for data science—such as Python or R—are not often the same programming languages that are used in production environments—such as C++ or C#. In circumstances when using the data science programming language is suitable, the data scientist must still clean up their notebook to remove unnecessary dependencies, dead-ends, and unused code in their exploration before exporting the notebook to a standalone script for execution in the production environments. In short, data scientists desire push-button approaches to productionize their notebooks.""",
        "Explore history": """Due to the affordance of out-of-order execution in computational notebooks, it can quickly—both unintentionally and intentionally—have an internal state that is different from the linear order of the notebook presented to the data scientist. This is one form of history-related pain point within a notebook. Without history support within the notebook, data scientists must painfully debug how their notebook entered the current state. As data scientists conduct exploration, build models, and evaluate multiple design options, they also introduce multiple notebooks into their environment, which they often manage in an ad-hoc way (for example, experiment_current.ipynb and experiment_old.ipynb). This is the other form of history-related pain point between notebooks. Without support for easily finding the right information across notebooks, data scientists end up reimplementing functionality or using stale data because they lose track of their notebooks.
In contrast to version control typically found in software engineering systems (git), preserving the history of artifacts is also important to data scientists. Novel innovations in the notebook space are required to support these unique requirements. For example, Head and colleagues found that data scientists do not want to spend up-front effort in managing code versions or organizing their code, and that data scientists prefer automated approaches to version control management.
As computational notebooks use both text and visual medium, advanced tools and techniques are required that can easily differentiate changes (both text and visual) between different versions of notebooks.
Finally, supporting annotations and comments in computational notebooks allows data scientists to catalog their thoughts and comments for decisions they've made in the notebook, essentially, a form of inline journaling.""",
        "Long-running tasks": """The scale of data and computation increases as data scientists incorporate more demanding activities into their computational notebooks. Activities previously offloaded to standalone scripts or jobs, like working with large datasets, are now routinely conducted within the notebook itself. These activities are enabled by big data libraries that are directly accessible in Python, such as tensorflow and keras, as well as through data connectors that give data scientists access to large data repositories from within the notebook. But large scale data means long-running computations, which often block operations in the underlying language kernel, creating tensions with the interactivity that data scientists expect from notebooks. For example, many data science libraries are synchronous, meaning that they block the data scientist from any other operations. And with streaming data—that is, data that is continuously generated by a data source—the program runs forever.
To support these activities, notebook developers must support scalable computations as a first-class design goal in notebooks. In other words, computational notebooks should maintain the benefits of exploration, interactivity, debugging, and visualization, irrespective of the size of the data.
Potential opportunities include transaction support, which allows the data scientist to abort long-running cells and revert to a safe state prior to executing the problematic cell. For streaming data, reactive notebooks such as BeakerX and Tempe automatically update computations as new data becomes available in the notebook. However, enabling interactivity and scaling requires careful design and introduces new challenges—in particular, these notebook models can exaggerate confusion data scientists already have with out-of-order execution.
""",
    }

    design_principles = [
        # Scheme
        "Achieve Expressiveness by Lifting Restrictions on Primitives: Programming languages should be designed not by piling feature on top of feature, but by removing the weaknesses and restrictions that make additional features appear necessary.",
        # Guy Steele
        "Languages Should be Extensible: I stand on this claim: I should not design a small language, and I should not design a large one. I need to design a language that can grow. I need to plan ways in which it might grow—but I need, too, to leave some choices so that other persons can make those choices at a later time.",
        # Josh Pollock (me)
        "Favor Programs Over Directed Acyclic Graphs (DAGs): When designing a new API for some specialized kind of programming (e.g. machine learning or build systems), we often start modeling the domain using a directed acyclic graph (DAG). But to increase the expressiveness of our APIs, we should let users write arbitrary programs.",
        # Michael Hicks
        "Strive for Abstractions That Are Both Simple and General: The ethos of PL research is to not just find solutions to important problems, but to find the *best expression of those solutions*, typically in the form of a kind of language, language extension, library, program analysis, or transformation. The hope is for *simple, understandable* solutions that are also *general*: By being part of (or acting at the level of) a language, they apply to many (and many sorts of) programs, and possibly many sorts of problems.",
        # Jared Roesch (paraphrased)
        "Encode Key Information in Your Program Representation: Compilers must explicitly represent the constructs they intend to optimize or reason about.",
    ]

    # answer = await ask(
    #     "Consider the pain points and programming languages design principles in the context. What are some ideas for how we can apply these design principles to address the pain points?",
    #     context=f"""
    #     ## Pain Points

    #     {pain_points}

    #     ## Programming Languages Design Principles

    #     {design_principles}
    #     """,
    #     debug=True,
    # )

    # answers = await async_map(
    #     list(zip(pain_points, [design_principles] * len(pain_points))),
    #     address_pain_point,
    # )

    answers = await async_map(
        list(zip(pain_points, [design_principles] * len(pain_points))),
        explore_root_cause,
    )

    # print(f"Answer: {answer}")
