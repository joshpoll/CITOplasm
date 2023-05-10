import asyncio
from httpx import HTTPStatusError
from ice.agents.openai import OpenAIAgent
from ice.apis.openai import (
    _post,
    TooLongRequestError,
    add_fields,
    get_davinci_equivalent_tokens,
)
from typing import (
    Optional,
    Mapping,
    Union,
)

import requests


async def openai_complete(
    prompt: str,
    desc: str,
    stop: Optional[str] = "\n",
    top_p: float = 1,
    temperature: float = 0,
    model: str = "text-davinci-002",
    max_tokens: int = 256,
    # logprobs: Optional[int] = None,
    logit_bias: Optional[Mapping[str, Union[int, float]]] = None,
    n: int = 1,
    # echo: bool = False,
    cache_id: int = 0,  # for repeated non-deterministic sampling using caching
) -> dict:
    """Send a completion request to the OpenAI API and return the JSON response."""
    params = {
        "model": model,
        #################################
        # this is a key line!
        #################################
        "messages": [
            # {"role": "system", "content": desc},
            # {"role": "user", "content": prompt},
            {"role": "system", "content": prompt},
        ],
        "temperature": temperature,
        "top_p": top_p,
        "n": n,
        "stop": stop,
        "max_tokens": max_tokens,
        # TODO: there are some other metadata fields that we can pass in...
        #################################
        # this are key lines!
        #################################
        # "echo": echo,
        # "logprobs": logprobs,
    }
    if logit_bias:
        params["logit_bias"] = logit_bias  # type: ignore[assignment]
    #################################
    # this is a key line!
    #################################
    # max_retries = 5
    # response = None
    # for i in range(max_retries):
    #     try:
    #         response = await _post("chat/completions", json=params, cache_id=cache_id)
    #     except requests.exceptions.HTTPError as err:
    #         if err.status == 500:  # Only retry if the status code is 500
    #             print(f"Request failed with {response.status}, retrying... {i + 1}")
    #             await asyncio.sleep(2**i)  # Exponential backoff
    #         else:
    #             raise err  # Re-raise the exception if status code is not 500
    # if response is None:
    #     raise Exception(
    #         "Max retries exceeded"
    #     )  # Raise exception if request failed even after max_retries
    response = await _post("chat/completions", json=params, cache_id=cache_id)
    if isinstance(response, TooLongRequestError):
        raise response
    add_fields(davinci_equivalent_tokens=get_davinci_equivalent_tokens(response))
    return response


class OpenAIChatAgent(OpenAIAgent):
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        desc: str = "",
        temperature: float = 0.0,
        top_p: float = 1.0,
    ):
        self.model = model
        self.desc = desc
        self.temperature = temperature
        self.top_p = top_p

    async def _complete(self, prompt, **kwargs) -> dict:
        """Send a completion request to the OpenAI API with the given prompt and parameters."""
        kwargs.update(
            {
                "model": self.model,
                "desc": self.desc,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "n": 1,
            }
        )
        try:
            response = await openai_complete(prompt, **kwargs)
        except HTTPStatusError as e:
            # throw the prompt in the error message
            raise Exception(f"{e}\nPrompt: {prompt}")
        if "choices" not in response:
            raise ValueError(f"No choices in response: {response}")
        return response

    def _extract_completion(self, response: dict) -> str:
        """Extract the answer text from the completion response."""
        return response["choices"][0]["message"]["content"].strip()
