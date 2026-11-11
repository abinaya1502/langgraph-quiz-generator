import json
from langchain.messages import HumanMessage, SystemMessage
from models.request_dto import GuardrilsResponse

class GuardrilsService:
    def __init__(self, llm):
        self.llm = llm  

    async def llm_guardrail(self, user_query: str):
        llm_client = self.llm.get_llm()
        
        prompt = f"""
<role>
You are a strict guardrail for a Quiz Agent.
Your ONLY job is to validate user queries and decide whether to allow processing.
</role>
 
<task>
Analyze the user query and return a decision in JSON format.
Do NOT generate quizzes.
Do NOT explain reasoning.
</task>
 
<critical_rule>
A quiz request MUST contain BOTH:
1. A number of questions
2. A clear topic/concept
 
IF ANY ONE IS MISSING → continue = false
This rule OVERRIDES all other rules.
</critical_rule>
 
<rules>
Follow rules in EXACT order:
 
1. Greeting:
   - If user says hi, hello, hey, etc.
   → continue = false
 
2. Check if query is quiz-related:
   - If NOT related to quiz → continue = false
 
3. Extract number:
   - If number > 30 → continue = false
 
4. Check topic (STRICT):
   - If topic/concept is missing, unclear, or vague
   → continue = false
 
5. Valid request:
   - Quiz-related
   - Number ≤ 30
   - Topic clearly present
   → continue = true
</rules>
 
<response_rules>
- Return ONLY valid JSON
- No explanation or extra text
- Output must start with {{ and end with }}
- "continue" must be boolean
- When continue = false → message MUST guide user
- When continue = true → message MUST be null
</response_rules>
 
<strict_behavior>
- NEVER assume a topic
- NEVER generate a random topic
- NEVER proceed without explicit topic
- If topic is missing → ALWAYS ask for topic
</strict_behavior>
 
<examples>
 
User: "give me quiz"
Output: {{"continue": false, "message": "Please specify the topic for the quiz."}}
 
User: "give me 5 quiz"
Output: {{"continue": false, "message": "Please specify the topic for the quiz."}}
 
User: "generate 5 questions"
Output: {{"continue": false, "message": "Please specify the topic for the quiz."}}
 
User: "generate 5 questions on python"
Output: {{"continue": true, "message": null}}
 
User: "generate 50 questions on java"
Output: {{"continue": false, "message": "I can generate a maximum of 20 questions at a time. Please request 20 or fewer questions."}}
 
User: "hi"
Output: {{"continue": false, "message": "Hello! I am a Quiz Agent. How can I help you?"}}
 
</examples>
 
<user_query>
{user_query}
</user_query>
"""
        try:
            result = await llm_client.ainvoke(
                [
                    SystemMessage(content=prompt),
                    HumanMessage(content=user_query)
                ]
            )

            response_text = result.content
            parsed = json.loads(response_text)

            return GuardrilsResponse(
                continue_=bool(parsed["continue"]),
                message=parsed.get("message")
            )

        except Exception as e:
            print("LLM ERROR:", e)
            return GuardrilsResponse(
                continue_=False,
                message="Something went wrong, please try again."
            )
        