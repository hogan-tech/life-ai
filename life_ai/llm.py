import os

from dotenv import load_dotenv

load_dotenv()


def is_available() -> bool:
    """Return True if at least one supported API key is present."""
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def complete(prompt: str, model: str = "claude-sonnet-4-6") -> str:
    provider = _detect_provider(model)

    if provider == "anthropic":
        return _anthropic(prompt, model)

    raise ValueError(f"Unsupported model: {model}")


def _detect_provider(model: str) -> str:
    if model.startswith("claude"):
        return "anthropic"
    raise ValueError(f"Cannot detect provider for model: {model}")


def _anthropic(prompt: str, model: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set")

    import anthropic  # deferred so missing package only errors at call time

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
