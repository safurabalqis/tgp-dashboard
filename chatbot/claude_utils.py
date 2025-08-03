import json

def prompt_claude_v3(client, user_prompt: str):
    body = {
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
        "anthropic_version": "bedrock-2023-05-31"
    }

    response = client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
