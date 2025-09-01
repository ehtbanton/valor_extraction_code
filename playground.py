


from src.text_processing import cleanup_response

response = f"```\n| Organization name | Prime Road Alternative (Cambodia) Company Limited || --- | --- |\n| Contact person | INFO_NOT_FOUND: Contact person |\n| Title | INFO_NOT_FOUND: Title |\n| Address | INFO_NOT_FOUND: Address |\n| Telephone | INFO_NOT_FOUND: Telephone |\n| Email | INFO_NOT_FOUND: The email address domain must match that of the organization. |\n```"
response = cleanup_response(response)

print(response)

exit()



from src.gemini_interface import setup_gemini, ask_gemini

GEMINI_AGENT = setup_gemini()
print("\nGemini agent setup complete.")
prompt = input("\nUser: ")

response = ask_gemini(GEMINI_AGENT, prompt)
print("\nGemini:")
print(response)


