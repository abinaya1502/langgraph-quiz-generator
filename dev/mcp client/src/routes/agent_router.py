from fastapi import APIRouter, Depends

from dependency.dependency import get_agent_service
from models.api_response_dto import APIResponse
from models.request_dto import QuizAgentRequest
from services.agent_service import AgentService
from utils.decorator import handle_errors
from utils.errors.error_log import log_error
from utils.errors.http_status import HttpStatusCode
from models.custome_app_exepction import CustomAppException
from utils.errors.error_codes import ErrorCode
from utils.logger import get_logger

logger = get_logger(__name__)

 
router = APIRouter(prefix="/api/v1")
 
 
@router.post("/quiz-agent")
@handle_errors("Router Error")
async def agent_router(request:QuizAgentRequest, service : AgentService = Depends(get_agent_service)):
    
    # try:
        
    logger.info("service function called")
    result = await service.agent_service(request = request)

    return APIResponse(
        data= result,
        code= HttpStatusCode.OK
    ).to_dict()

 
    # except Exception as e:
    #     log_error("agent_router.py","router",str(e))
    #     raise CustomAppException(
    #         message=f"Router error: {str(e)}",
    #         code=ErrorCode.INTERNAL_SERVER_ERROR,
    #         status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
            
    #     )
 