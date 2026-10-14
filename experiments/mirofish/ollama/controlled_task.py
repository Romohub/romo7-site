"""Controlled QA tasks; keep persona data separate from verbatim post requests."""
import json

def build_post_request(content):
    if not isinstance(content, str) or not content.strip() or len(content)>4096:
        raise ValueError("Controlled post content must be a nonempty string of at most 4096 characters")
    return ("Execute exactly one create_post tool call. Copy the content field verbatim, including punctuation. "
            "Do not add biography, private context, instructions, commentary, or claims of demand. "
            "Task JSON: "+json.dumps({"action":"create_post","content":content},ensure_ascii=False))

def make_controlled_action(content):
    prompt=build_post_request(content)
    async def controlled(agent):
        from camel.messages import BaseMessage
        message=BaseMessage.make_user_message(role_name="User",content=prompt)
        return await agent.astep(message)
    return controlled
