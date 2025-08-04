
from llama_interface import setup_llama, ask_llama

# Adjust model path and parameters as needed
model_path = "F:\\_llm_models\\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" # Meta Llama 3.1 8B model
#model_path = "F:\\_llm_models\\Qwen3-32B-Q4_K_M.gguf" # qwen 3 reasoning model
LLAMA_CLIENT = setup_llama(model_path, n_gpu_layers=-1, n_ctx=10000)

while True:
    prompt = input("\n\nEnter a prompt: " )
    response = ask_llama(LLAMA_CLIENT, prompt)
    print("\nLLM response:", response)