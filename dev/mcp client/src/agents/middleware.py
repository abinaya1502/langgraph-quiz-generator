from typing import Callable, Awaitable
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse

from tools.quiz_agent import quiz_agent
from tools.review_agent import review_agent

STEP_TOOLS = {
    "quiz_agent":[quiz_agent],
    "review_agent": [review_agent],
    "done": []
}


class RouteByStepMiddleware(AgentMiddleware):
    
    async def awrap_model_call(self,request: ModelRequest,handler: Callable[[ModelRequest], Awaitable[ModelResponse]],) -> ModelResponse:
        """Async version used when ainvoke() is called."""
        current_step = request.state.get("current_step", "quiz_agent")
        allowed_tools = STEP_TOOLS.get(current_step)
        if  allowed_tools is None:
            raise ValueError(f"Unknown step: '{current_step}'")
        request = request.override(tools=allowed_tools)
        return await handler(request)



route_by_step = RouteByStepMiddleware()