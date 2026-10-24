import httpx
from fastapi import FastAPI, Request 
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.database import create_conversation, save_message, get_all_messages, get_summary, save_summarized_through_id, get_summarized_through_id, save_summary
from backend.context_manager import split_by_token_budget, summarize_messages

TOKEN_BUDGET = 800 # A rough estimate of how many tokens we can send to Ollama at once. This is a safeguard against sending too much data and overwhelming the model.

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:4b" # Main Model is rhy:latest, the small qwen2.5:0.5b model or gemma:2b or qwen3.5:4b is for faster testing and development.

# Mount: everything under this URL prefix maps directly to files in this folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# When someone requests the root URL with GET, This function runs
@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()         # Parse incoming JSON data
    user_message = data["message"]      # Extract the user's message from the JSON
    conversation_id = data.get("conversation_id")  # Get conversation ID if provided

    # Figure out which conversation this belongs to
    if conversation_id is None:
        conversation_id = create_conversation()  # Create a new conversation if none exists
        print(f"[DEBUG] New conversation created with ID: {conversation_id}")

    # Save the user's message to the database
    save_message(conversation_id, "user", user_message) 

    all_messages = get_all_messages(conversation_id)  # Retrieve all messages for this conversation
    print (f"[DEBUG] Total messages in conversation: {len(all_messages)}")  # Debugging: print how many messages are in the conversation
    old_messages, recent_messages = split_by_token_budget(all_messages, TOKEN_BUDGET)  # Split messages based on token budget
    print (f"[DEBUG] Split result - old: {len(old_messages)}, recent: {len(recent_messages)}")  # Debugging: print how many messages are old vs recent

    if old_messages:
        already_summarized_id = get_summarized_through_id(conversation_id)
        new_old_messages = [m for m in old_messages if m["id"] > already_summarized_id]

        if new_old_messages:
            current_summary = get_summary(conversation_id)
            print(f"[DEBUG] Current summary: {current_summary}")  # Debugging: print the current summary
            updated_summary = await summarize_messages(MODEL_NAME, current_summary, new_old_messages)
            print(f"[DEBUG] Updated summary: {updated_summary}")  # Debugging: print the updated summary
            save_summary(conversation_id, updated_summary)
            save_summarized_through_id(conversation_id, new_old_messages[-1]["id"])
        else:
            updated_summary = get_summary(conversation_id)

        history = [{"role": "user", "content": f"Summary of earlier conversation: {updated_summary}"}] + recent_messages
    else:
        print("[DEBUG] No old messages to summarize. Using recent messages only.")  # Debugging: indicate that there are no old messages
        history = recent_messages

    print(f"[DEBUG] Final history sent to Ollama: ({len(history)} messages)")  # Debugging: print how many messages are being sent to Ollama
    for m in history:
        print(f"    {m['role']}: {m['content'][:60]}") # truncate long content for readability

    """
    # Old code block for sending entire message history to Ollama on every request. 

    # Build full history for Ollama (Gives memory to the model)
    # Already includes user's latest message to avoid duplication and seamless flow
    history = get_messages_for_conversation(conversation_id)
    print(f"Sending {len(history)} messages to Ollama")  # Debugging: print how many messages are being sent
    """

    # Opens a connnection and sends full history, not just latest message
    async with httpx.AsyncClient(timeout=120) as client:
        # Sends request to Ollama and waits for its reponse
        response = await client.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "messages": history,
            "stream": False
        })

    # Parses the JSON response from Ollama
    result = response.json()
    # Debugging: print the full response
    print("Received from Ollama: ", result)
    # API's chosen structure
    reply = result["message"]["content"]

    # Save Rhy's reply to database
    save_message(conversation_id, "assistant", reply)

    return {"reply": reply, "conversation_id": conversation_id}

