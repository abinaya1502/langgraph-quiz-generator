
from langchain.agents import create_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from models.request_dto import QuizAgentResponse
from models.custome_app_exepction import CustomAppException
from utils.decorator import handle_errors
from utils.errors.error_codes import ErrorCode
from utils.errors.error_log import log_error
from utils.errors.http_status import HttpStatusCode
from utils.llm_client import Llm
from utils.logger import get_logger
from setting import config

logger = get_logger(__name__)

# DB_URI = (
#     f"postgresql://{config.db_username}:"
#     f"{config.db_password}@"
#     f"{config.db_host}:"
#     f"{config.db_port}/"
#     f"agent_as_tool_db"
# )


# llm = Llm()

class QuizAgent:
    def __init__(self,llm : Llm):
        self.llm = llm
    @handle_errors("Quiz Agent creation error")
    async def quiz_run_agent(self,checkpointer):
        # try:
            llm_client = self.llm.get_llm()
        

            
            agent = create_agent(
                model=llm_client,
                tools=[],
                checkpointer=checkpointer,
                response_format=QuizAgentResponse,
            )
            return agent
            

        # except Exception as e:
        #     log_error("quiz_run_agent.py", "quiz_run_agent", str(e))
        #     raise CustomAppException(
        #         message=f"Quiz Agent creation error: {str(e)}",
        #         code=ErrorCode.INTERNAL_SERVER_ERROR,
        #         status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
        #     )