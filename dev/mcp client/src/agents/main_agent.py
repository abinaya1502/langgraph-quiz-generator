from langchain.agents import create_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import HumanMessage, SystemMessage
from agents.main_prompt import MainSystemPrompt
from agents.middleware import route_by_step
from agents.state import AgentState
from models.custome_app_exepction import CustomAppException
from models.request_dto import QuizAgentRequest, ReviewAgentResponse
from utils.decorator import handle_errors
from utils.errors.error_codes import ErrorCode
from utils.errors.error_log import log_error
from utils.errors.http_status import HttpStatusCode
from utils.llm_client import Llm
from utils.logger import get_logger
from tools.quiz_agent import quiz_agent
from tools.review_agent import review_agent
from setting import config_db

logger = get_logger(__name__)

# DB_URI = (
#     f"postgresql://{config.db_username}:"
#     f"{config.db_password}@"
#     f"{config.db_host}:"
#     f"{config.db_port}/"
#     f"agent_as_tool_db"
# )
DB_URI = config_db


class MainAgent:
    def __init__(self,llm: Llm,prompt: MainSystemPrompt):
        self.prompt =prompt
        self.llm = llm
    @handle_errors("Main Agent Error")
    async def main_agent(self, request: QuizAgentRequest) -> ReviewAgentResponse:
        # try:
            llm_client = self.llm.get_llm()
            system_prompt = self.prompt.get_system_prompt()

            async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
                await checkpointer.setup()
                agent = create_agent(
                    model=llm_client,
                    tools=[quiz_agent, review_agent],
                    checkpointer=checkpointer,
                    state_schema=AgentState,
                    response_format=ReviewAgentResponse,
                    middleware=[route_by_step],
                )

                initial_state = {
                    "messages": [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=(
                            # f"Start a quiz for the user.\n"
                            # f"Concept: {request.concept}\n"
                            # f"Difficulty: {request.level}\n"
                            # f"Number of questions: {request.no_of_questions}\n"
                            f"User ID: {request.user_id}\n\n"
                            f"User Query: {request.user_query}\n"
                            f"First call quiz_agent, then after answers are "
                            f"collected call review_agent using the state."
                        )),
                    ],
                    "current_step":    "quiz_agent",
                    # "concept":         request.concept,
                    # "level":           request.level,
                    # "no_of_questions": request.no_of_questions,
                    "user_query": request.user_query,
                    "user_id":         request.user_id,
                }

                result = await agent.ainvoke(
                    initial_state,
                    {"configurable": {"thread_id": str(request.user_id)}},
                )

                output = result["structured_response"]
                logger.debug(f"Main agent final output:\n{output}")
                return output

        # except Exception as e:
        #     log_error("main_agent.py", "main_agent", str(e))
        #     raise CustomAppException(
        #         message=f"Main Agent error: {str(e)}",
        #         code=ErrorCode.INTERNAL_SERVER_ERROR,
        #         status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
        #     )