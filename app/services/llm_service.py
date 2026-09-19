import ollama


MODEL_NAME = "llama3.1:8b"


def generate(prompt: str) -> str:

    print(f"\n[OLLAMA] Model: {MODEL_NAME}")
    print("[OLLAMA] Generating response...")

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    print("[OLLAMA] Response received.")

    return response["message"]["content"]