from fvalues import F

from ice.recipe import recipe


def make_verification_prompt(question: str, answer: str) -> str:
    return F(
        f"""Consider these two quotes:
Quote 1: "{question}"

Quote 2: "{answer}"

Q: Do they mean approximately the same thing? Say "A: Yes" or "A: No".
A:"""
    )


def make_gt_verification_prompt(quote1: str, quote2: str) -> str:
    return F(
        f"""Consider these two quotes:
Quote 1: "{quote1}"

Quote 2: "{quote2}"

Q: Is the first quote at least as informative as the second? Say "A: Yes" or "A: No".
A:"""
    )


async def verify_answer(question: str, answer: str) -> float:
    prompt = make_verification_prompt(question=question, answer=answer)
    choice_probs, _ = await recipe.agent().classify(
        prompt=prompt, choices=(" Yes", " No")
    )
    return choice_probs.get(" Yes", 0)


async def verify_gt_answer(str1: str, str2: str) -> float:
    prompt = make_gt_verification_prompt(str1, str2)
    choice_probs, _ = await recipe.agent().classify(
        prompt=prompt, choices=(" Yes", " No")
    )
    return choice_probs.get(" Yes", 0)


class ApproximateEqualityError(AssertionError):
    def __init__(self, str1, str2):
        super().__init__(
            f"Strings not approximately equal:\nExpected: {str2}\nActual  : {str1}"
        )


class ApproximateCmpError(AssertionError):
    def __init__(self, str1, str2):
        super().__init__(
            f"Actual string not at least as informative as expected:\nExpected: {str2}\nActual  : {str1}"
        )


# TODO: these comparisons may need to include context to more accurately assess the outputs


async def approx_eq(str1, str2, threshold: float = 0.7):
    if not await verify_answer(str1, str2) >= threshold:
        raise ApproximateEqualityError(str1, str2)
    return True


async def approx_gt(str1, str2, threshold: float = 0.7):
    res = await verify_gt_answer(str1, str2)
    # print(res)
    if not res >= threshold:
        raise ApproximateCmpError(str1, str2)
    return True
