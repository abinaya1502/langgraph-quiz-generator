from langchain.agents import create_agent

from langgraph.graph import END

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from models.custome_app_exepction import CustomAppException
from models.request_dto import ReviewAgentResponse
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

class ReviewAgent:
    def __init__(self, llm: Llm):
        self.llm = llm
    @handle_errors("Reviewer Agent creation error")
    async def review_run_agent(self,checkpointer):
        # try:
            
        
            llm_client = self.llm.get_llm()
            
            
            agent = create_agent(
                model=llm_client,
                tools=[],
                checkpointer=checkpointer,
                response_format=ReviewAgentResponse,
            )
            return agent

        # except Exception as e:
        #     log_error("review_run_agent.py", "review_run_agent", str(e))
        #     raise CustomAppException(
        #         message=f"Reviewer Agent creation error: {str(e)}",
        #         code=ErrorCode.INTERNAL_SERVER_ERROR,
        #         status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
        #     )