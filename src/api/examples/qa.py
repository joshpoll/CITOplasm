from src.api.defs import *


async def qa(question: str) -> str:
    return await ask(question)


async def qa_with_context(question: str, context: str) -> str:
    return await ask(question, context=context)
