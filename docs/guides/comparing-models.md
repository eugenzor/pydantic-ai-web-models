---
icon: lucide/git-compare
---

# Comparing Models

Because each `Agent` call is independent and non-blocking, you can run the same prompt against
multiple models concurrently using `asyncio.gather`. This is useful for benchmarking response
quality, comparing latency, or picking the best model for a given task.

## Concurrent Model Comparison

```python title="compare_models.py"
import asyncio
from pydantic_ai import Agent
import pydantic_ai_web_models

MODELS = [
    "google-web:gemini-3-flash",
    "google-web:gemini-3.1-pro",
    "openai-web:gpt-5-3",
    "openai-web:gpt-5-4-standard",
]


async def ask_model(model: str, prompt: str) -> str:
    agent = Agent(model=model)
    result = await agent.run(prompt)
    return result.data


async def main():
    prompt = "In exactly one sentence, what is the meaning of life?"

    tasks = [ask_model(m, prompt) for m in MODELS]
    responses = await asyncio.gather(*tasks)

    for model, response in zip(MODELS, responses):
        print(f"[{model}]:")
        print(f"  {response}")
        print()


asyncio.run(main())
```

All four workflow executions are dispatched concurrently to Temporal. Each one runs in its own
Temporal workflow on the worker, so they complete in parallel and the total wall-clock time is
roughly equal to the slowest individual model rather than their sum.

!!! tip "Comparing structured output quality"
    The comparison pattern works equally well with `output_type`. Pass the same Pydantic model
    to each `Agent` to compare how consistently different models conform to a schema:

    ```python title="compare_structured.py"
    import asyncio
    from pydantic import BaseModel
    from pydantic_ai import Agent
    import pydantic_ai_web_models

    MODELS = [
        "google-web:gemini-3-flash",
        "openai-web:gpt-5-4-standard",
    ]


    class MovieReview(BaseModel):
        title: str
        rating: float  # 1.0 – 10.0
        pros: list[str]
        cons: list[str]
        verdict: str


    async def ask_model(model: str, prompt: str) -> MovieReview:
        agent = Agent(model=model, output_type=MovieReview)
        result = await agent.run(prompt)
        return result.data


    async def main():
        prompt = "Review the movie Inception (2010)."
        tasks = [ask_model(m, prompt) for m in MODELS]
        reviews = await asyncio.gather(*tasks)

        for model, review in zip(MODELS, reviews):
            print(f"[{model}] — {review.title} ({review.rating}/10)")
            print(f"  Pros: {', '.join(review.pros)}")
            print(f"  Cons: {', '.join(review.cons)}")
            print()


    asyncio.run(main())
    ```

    This makes it easy to spot which model produces more complete, correctly typed responses for
    your specific domain.
