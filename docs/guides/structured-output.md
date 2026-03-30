---
icon: lucide/braces
---

# Structured Output

Pass `output_type=MyModel` to `Agent` and the library will instruct the LLM to respond with
JSON matching your Pydantic model's schema. The response is automatically extracted, parsed, and
validated before being returned to your code.

## Basic Example

```python title="basic_structured.py"
from pydantic import BaseModel
from pydantic_ai import Agent
import pydantic_ai_web_models


class CityInfo(BaseModel):
    name: str
    country: str
    population: int
    famous_for: list[str]


agent = Agent(
    model="google-web:gemini-3-flash",
    output_type=CityInfo,
)
result = agent.run_sync("Tell me about Tokyo.")
city = result.data

print(f"{city.name}, {city.country}")
print(f"Population: {city.population:,}")
print(f"Famous for: {', '.join(city.famous_for)}")
# Tokyo, Japan
# Population: 13,960,000
# Famous for: cherry blossoms, Shibuya crossing, sushi, anime
```

## Nested Models

Pydantic nested models work exactly as you would expect. The JSON schema sent to the LLM
includes the full nested structure.

```python title="nested_models.py"
from pydantic import BaseModel
from pydantic_ai import Agent
import pydantic_ai_web_models


class Address(BaseModel):
    street: str
    city: str
    country: str


class Person(BaseModel):
    name: str
    age: int
    occupation: str
    address: Address


agent = Agent(
    model="openai-web:gpt-5-4-standard",
    output_type=Person,
)
result = agent.run_sync(
    "Generate a fictional person living in Berlin who works as a software engineer."
)
person = result.data

print(f"{person.name}, age {person.age}")
print(f"Works as: {person.occupation}")
print(f"Lives at: {person.address.street}, {person.address.city}")
```

## Enums and Optional Fields

Pydantic models with `Enum` fields and optional attributes (using `| None`) are fully supported.

```python title="enums_optional.py"
from enum import Enum
from pydantic import BaseModel
from pydantic_ai import Agent
import pydantic_ai_web_models


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ReviewAnalysis(BaseModel):
    sentiment: Sentiment
    confidence: float
    key_topics: list[str]
    summary: str
    improvement_suggestion: str | None = None


agent = Agent(
    model="openai-web:gpt-5-4-standard",
    output_type=ReviewAnalysis,
)
result = agent.run_sync(
    "Analyze this review: 'The food was amazing but the service was incredibly slow. "
    "We waited 45 minutes for our appetizers. The dessert almost made up for it though.'"
)
analysis = result.data

print(f"Sentiment: {analysis.sentiment.value} ({analysis.confidence:.0%})")
print(f"Topics: {', '.join(analysis.key_topics)}")
print(f"Summary: {analysis.summary}")
if analysis.improvement_suggestion:
    print(f"Suggestion: {analysis.improvement_suggestion}")
```

??? info "How structured output works internally"

    When `output_type` is set on an `Agent`, the library appends a JSON schema instruction to
    the end of the prompt before sending it to the Temporal workflow. The instruction looks
    roughly like:

    ```
    Respond with a JSON object matching this schema:
    {"type": "object", "properties": {...}, "required": [...]}
    Do not include any text outside the JSON object.
    ```

    When the workflow response arrives, the library tries three strategies to extract valid JSON,
    in order:

    1. **Direct parse** — attempt `json.loads(response_text)` on the full response as-is.
    2. **Strip markdown fences** — if the response is wrapped in ` ```json ... ``` ` or ` ``` ... ``` `,
       strip the fences and attempt `json.loads` again.
    3. **Find outermost braces** — scan the string for the first `{` and the last `}`, extract
       that substring, and attempt `json.loads` one final time.

    If all three strategies fail, a `JSONParseError` is raised with the raw response text
    available as `e.raw_text`.

    Once a JSON object is successfully extracted it is validated against the Pydantic model,
    and then wrapped in a tool-call response so that pydantic-ai's internal machinery can
    unwrap it cleanly.

!!! warning "Handling `JSONParseError`"

    Occasionally an LLM will produce a response that cannot be parsed as JSON despite the
    schema instruction. Always wrap structured-output calls with a `try/except` for production
    code:

    ```python
    from pydantic_ai import Agent
    from pydantic_ai_web_models import JSONParseError
    import pydantic_ai_web_models

    agent = Agent(model="google-web:gemini-3-flash", output_type=CityInfo)

    try:
        result = agent.run_sync("Tell me about Paris.")
        city = result.data
    except JSONParseError as e:
        print(f"Could not parse JSON response: {e}")
        print(f"Raw LLM response was:\n{e.raw_text[:500]}")
    ```
