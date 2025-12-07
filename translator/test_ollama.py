import subprocess
import json

prompt = "Say a single fictional word."

result = subprocess.run(
  ["ollama", "generate", "llama3", "--json"],
  input=prompt.encode(),
  stdout=subprocess.PIPE,
  stderr=subprocess.PIPE
)

# Parse streaming JSON
output = ""
for line in result.stdout.decode().splitlines():
  try:
    j = json.loads(line)
    output += j.get("response", "")
  except:
    pass

print("Model output:", output.strip())