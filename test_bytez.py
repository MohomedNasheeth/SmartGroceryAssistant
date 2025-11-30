from bytez import Bytez

# Initialize
key = "c34ee9824b16cec9a0837b7e66aad9f4"
sdk = Bytez(key)
model = sdk.model("Qwen/Qwen3-0.6B")

# Test the API
print("Testing Bytez API...")
print("=" * 60)

result = model.run([
    {
        "role": "user",
        "content": "Say hello in one word"
    }
])

print("Type of result:", type(result))
print("Result:", result)
print("=" * 60)

# Check what we got
if isinstance(result, tuple):
    print("It's a TUPLE")
    print("Length:", len(result))
    if len(result) == 2:
        output, error = result
        print("Output:", output)
        print("Error:", error)
elif isinstance(result, dict):
    print("It's a DICT")
    print("Keys:", result.keys())
    print("Content:", result)
else:
    print("It's something else:", type(result))
    print("Content:", result)