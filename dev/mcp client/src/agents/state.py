from typing import Literal, List
from typing_extensions import NotRequired
from langgraph.graph import MessagesState
from models.request_dto import QuizQuestion

AgentStep = Literal["quiz_agent", "review_agent"]


class AgentState(MessagesState):
    current_step: NotRequired[AgentStep]
    # concept: NotRequired[str]
    # level: NotRequired[str]
    # no_of_questions: NotRequired[int]
    user_query: NotRequired[str]
    user_id: NotRequired[str]
    questions: NotRequired[List[QuizQuestion]]
    user_answers: NotRequired[List[str]]