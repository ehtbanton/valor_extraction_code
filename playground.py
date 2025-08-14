


from gemini_interface import setup_gemini, ask_gemini

gemini_agent = setup_gemini()
print("\nGemini agent setup complete.")
prompt = input("\nUser: ")
response = ask_gemini(gemini_agent, prompt)
print("\nGemini:")
print(response)
