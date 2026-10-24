import subprocess
import httpx
import asyncio

OLLAMA_URL = "http://localhost:11434"
_ollama_process = None  # module-level handle; None means "we didn't start it"


async def is_ollama_running() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OLLAMA_URL, timeout=2)
            return response.status_code == 200
    except httpx.RequestError:
        return False


def _launch_ollama_process():
    global _ollama_process
    _ollama_process = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


async def ensure_ollama_running(timeout_seconds: int = 15) -> bool:
    """
    Makes sure Ollama is reachable before we continue.
    Starts it if needed, then waits (polls) until it responds
    or we give up after timeout_seconds.
    """
    if await is_ollama_running():
        print("Ollama already running.")
        return True

    print("Ollama not running — starting it...")
    _launch_ollama_process()

    waited = 0
    while waited < timeout_seconds:
        if await is_ollama_running():
            print(f"Ollama is up after {waited}s.")
            return True
        await asyncio.sleep(0.5)    # Async Friendly version of time.sleep()
        waited += 0.5

    print("Ollama did not start in time.")
    return False


def stop_ollama():
    global _ollama_process
    if _ollama_process is not None:
        print("Stopping Ollama (we started it).")
        _ollama_process.terminate()
        _ollama_process.wait()
        _ollama_process = None