from typing import Annotated
from langgraph.types import Command
from langgraph.graph import END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain.tools import InjectedState, InjectedToolCallId, tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from agents.review_run_agent import ReviewAgent
from tools.review_prompt import ReviewSystemPrompt
from models.custome_app_exepction import CustomAppException
from models.request_dto import ReviewAgentResponse, ReviewAgentRequest, QuizQuestion
from utils.bedrock_client import Bedrock
from utils.decorator import handle_errors
from utils.errors.error_codes import ErrorCode
from utils.errors.error_log import log_error
from utils.errors.http_status import HttpStatusCode
from utils.llm_client import Llm
from utils.logger import get_logger
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
prompt = ReviewSystemPrompt()
review = ReviewAgent(Llm(Bedrock()))

@tool
@handle_errors("Reviewer Agent error")
async def review_agent(user_id: str,tool_call_id: Annotated[str, InjectedToolCallId],state: Annotated[dict, InjectedState],) -> Command:
        """
        Reviews quiz answers and returns score, grade, and feedback.
        Reads questions and user_answers from state automatically.
        Only requires user_id as input.
        """
    # try:
        questions_raw = state.get("questions", [])
        user_query = state.get("user_query","")
        user_answers  = state.get("user_answers", [])
        # concept       = state.get("concept", "")
        # level         = state.get("level", "")

        logger.info(f"review_agent | questions: {questions_raw}")
        logger.info(f"review_agent | user_answers: {user_answers}")

        parsed_questions = []
        for q in questions_raw:
            if isinstance(q, dict):
                parsed_questions.append(QuizQuestion(
                    question=q.get("question", ""),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", ""),
                ))
            else:
                parsed_questions.append(q)

        parsed_answers = []
        for a in user_answers:
            if isinstance(a, str):
                parsed_answers.append(a.strip().upper())
            elif isinstance(a, dict):
                parsed_answers.append(a.get("answer", "A").strip().upper())
            else:
                parsed_answers.append(str(a).strip().upper())

        review_request = ReviewAgentRequest(
            user_id=user_id,
            # concept=concept,
            # level=level,
        
            questions=parsed_questions,
            user_answers=parsed_answers,
        )
#         review_query = (
#     # f"Concept: {review_request.concept}\n"
#     # f"Difficulty: {review_request.level}\n\n"
#     f"The user query is {user_query}\n"
#     f"Evaluate each question one by one:\n\n"
#     + "\n".join(
#         f"Q{i+1}. {q.question}\n"
#         f"   User answer: {review_request.user_answers[i] if i < len(review_request.user_answers) else 'No answer'}\n"
#         f"   Correct answer: {q.correct_answer}\n"
#         f"   Match: {'YES' if i < len(review_request.user_answers) and review_request.user_answers[i] == q.correct_answer else 'NO'}\n"
#         for i, q in enumerate(review_request.questions)
#     )
#     + "\n\nNow count correct (Match=YES) and wrong (Match=NO) and format the response.\n"
#     f"Return: correct count, wrong count, grade,\n "
#     f"explanation for each wrong answer, and overall feedback."
# )
      

        review_query = (
            f"The user query is {user_query}\n"
            f"Evaluate each question using ONLY the Match field below:\n\n"
            + "\n".join(
                f"Q{i+1}. {q.question}\n"
                f"   User answer: {review_request.user_answers[i] if i < len(review_request.user_answers) else 'No answer'}\n"
                f"   Correct answer: {q.correct_answer}\n"
                f"   Match: {'YES' if i < len(review_request.user_answers) and review_request.user_answers[i].strip().upper() == q.correct_answer.strip().upper() else 'NO'}\n"
                for i, q in enumerate(review_request.questions)
            )
            + "\n\nRules:\n"
            + "- Count Match=YES for correct_count\n"
            + "- Count Match=NO for wrong_count\n"
            + "- ONLY add Match=NO questions to wrong_explanations\n"
            + "- wrong_explanations length MUST equal wrong_count exactly\n"
            + "- DO NOT re-evaluate answers, trust Match field only\n"
        )
        system_prompt = prompt.get_system_prompt()
        async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
            await checkpointer.setup()
            agent = await review.review_run_agent(checkpointer)
            result = await agent.ainvoke(
                {"messages": [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=review_query),
                ]},
                {"configurable": {"thread_id": f"{user_id}"}},
            )
            output = result["structured_response"]
            logger.debug(f"Review agent output:\n{output}")

            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=output.model_dump_json(), # toolmessage requires string , output is pydantic response so converted to json string
                            tool_call_id=tool_call_id,
                        )
                    ],
                    "current_step": "done",
                },
                goto=END,
            )

    # except Exception as e:
    #     log_error("review_agent.py", "review_agent", str(e))
    #     raise CustomAppException(
    #         message=f"Reviewer Agent error: {str(e)}",
    #         code=ErrorCode.INTERNAL_SERVER_ERROR,
    #         status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
    #     )
  