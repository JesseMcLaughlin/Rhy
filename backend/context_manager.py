import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"


def estimate_tokens(text):
    return len(text) // 4  # Rough estimate: 1 token ≈ 4 characters

def split_by_token_budget(messages, token_budget):
    recent_messages = []
    running_total = 0

    for message in reversed(messages):
        message_tokens = estimate_tokens(message["content"])

        if running_total + message_tokens > token_budget:
            print(f"[DEBUG] Budget Exceeded at {running_total + message_tokens} tokens -- STOP HERE")
            break

        recent_messages.insert(0, message)
        running_total += message_tokens
    print(f"[DEBUG] final running_total: {running_total} tokens across {len(recent_messages)} messages")

    cutoff_index = len(messages) - len(recent_messages)
    # List slicing syntax: list[start:end] returns a a sublist. removing start  ie list[:end] defaults to the very beginning of the list
    # So this means give me all messages up to the cutoff index
    old_messages = messages[:cutoff_index]

    return old_messages, recent_messages

async def summarize_messages(model_name, old_summary, messages_to_summarize):
    # Conjoins formatted strings into a single string, includes role and content of each message, separated by newlines
    # ie. user: Hello and assistant: Hello 
    text_block = "\n".join(f"{m['role']}: {m['content']}" for m in messages_to_summarize)

    prompt = (
        f"Existing summary of conversation so far:\n{old_summary}\n\n"
        f"New messages to incorporate:\n{text_block}\n\n"
        "Write a new, concise summary of the entire conversation so far, "
        "preserving important facts, names, and context."
    )

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(OLLAMA_URL, json={
            "model": model_name,
            "messages": [{"role": "system", "content": prompt}],
            "stream": False
        })

    result = response.json()
    return result["message"]["content"]