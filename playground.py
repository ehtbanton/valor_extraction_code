


from src.gemini_interface import setup_gemini, ask_gemini

GEMINI_AGENT = setup_gemini()
print("\nGemini agent setup complete.")
prompt = input("\nUser: ")

response = ask_gemini(GEMINI_AGENT, prompt)
print("\nGemini:")
print(response)

