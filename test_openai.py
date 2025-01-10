import openai 

# Hardcoded OpenAI API Key
openai.api_key = "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"  # Replace with your actual API key

# Test OpenAI Chat API Call
try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Replace with "gpt-4" if you have access
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        max_tokens=20
    )

    # Accessing the message content correctly
    print("✅ OpenAI API Test Successful!")
    print("Response:", response.choices[0].message.content.strip())

# Error Handling
except openai.AuthenticationError:
    print("❌ Authentication failed. Check your OpenAI API key.")
except openai.RateLimitError:
    print("❌ Rate limit exceeded. Try again later.")
except Exception as e:
    print(f"❌ An error occurred: {e}")
