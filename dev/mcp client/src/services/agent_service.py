
import uuid
from agents.main_agent import MainAgent
from setting import config
from langgraph.types import Command
from models.request_dto import QuizAgentRequest
from utils.decorator import handle_errors
from utils.errors.error_log import log_error
from utils.errors.http_status import HttpStatusCode
from models.custome_app_exepction import CustomAppException
from utils.errors.error_codes import ErrorCode
from utils.llm_client import Llm

from utils.logger import get_logger

logger = get_logger(__name__)

class AgentService:
    def __init__(self,agent,guardrils):
        self.agent = agent
        self.guardrils = guardrils
        
    @handle_errors("Service Error")
    async def agent_service(self, request: QuizAgentRequest):
        # try:
            decision = await self.guardrils.llm_guardrail(request.user_query)
            if not decision.continue_:
                 return {
                      "message" : decision.message
                 }

            thread_id = request.user_id or str(uuid.uuid4())
            request = QuizAgentRequest(user_id= thread_id,
                                       user_query= request.user_query)
            result = await self.agent.main_agent(request)
           
         
            print("  RESULTS")
            print("________________________________________________" )
            print(f"Correct: {result.correct_count}")
            print(f"Wrong: {result.wrong_count}")
            print(f"Grade: {result.grade}")

            if result.wrong_explanations:
                print("\n  Wrong answer explanations:")
                print("________________________________________________")
                for i, w in enumerate(result.wrong_explanations, 1):
                    print(f"\n  {i}. {w.question}")
                    print(f"Your answer: {w.user_answer}")
                    print(f"Correct: {w.correct_answer}")
                    print(f"Explanation: {w.explanation}")

            print("\n" +"________________________________________________")
            print(f" Feedback: {result.feedback}")
           

            return result
                   
           
            

        # except Exception as e:
        #     log_error("code_agent_service.py", "coder_agent_service", str(e))
        #     raise CustomAppException(
        #         message=f"Service error: {str(e)}",
        #         code=ErrorCode.INTERNAL_SERVER_ERROR,
        #         status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
        #     )
