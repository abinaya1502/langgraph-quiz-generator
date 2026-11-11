from typing import Annotated

from langchain.tools import InjectedToolCallId, tool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from agents.quiz_run_agent import QuizAgent
from models.request_dto import QuizAgentResponse
from tools.quiz_prompt import QuizSystemPrompt
from models.custome_app_exepction import CustomAppException
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
prompt = QuizSystemPrompt()
quiz = QuizAgent(Llm(Bedrock()))



@tool
@handle_errors("Quiz Agent error")
async def quiz_agent(user_query : str,user_id: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
        """
        Generates quiz questions with options for the given concept and difficulty.
        Prints questions to terminal, collects user answers, then hands off to review_agent.
        """
    # try:
        system_prompt = prompt.get_system_prompt()
        async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
            await checkpointer.setup()
            agent  = await quiz.quiz_run_agent(checkpointer)
            
            # query = (
            #     f"Generate {no_of_questions} quiz questions on '{concept}' "
            #     f"at {level} difficulty. Provide 4 options (A/B/C/D) for each."
            # )
            messages = [
                SystemMessage(content=system_prompt),HumanMessage(content=f"User Query: {user_query}"),]
            result = await agent.ainvoke(
                {"messages": messages},
                {"configurable": {"thread_id": user_id}},
            )
            output: QuizAgentResponse = result["structured_response"]
            print(output)
            logger.debug(f"Quiz agent output:\n{output}")

            user_answers = []

            # print("\n" + "________________________________________________"+"\n")a
            # print(f"QUIZ - {concept.upper()} - Level: {level}")
            print("\n" +"________________________________________________")
            for i, q in enumerate(output.questions, 1):
                print(f"\nQ{i}. {q.question}")
                for opt in q.options:
                    print(f"     {opt}")
                max_attempts = 5
                attempt = 0
                ans = input("Your answer (A/B/C/D): ").strip().upper()
                
                while ans not in ["A","B","C","D"]:
                    attempt += 1
                    if attempt >= max_attempts:
                        ans = None
                        print("Too Many Ivalid attempts.Skipping the question")
                        break
                    ans = input("Invalid! Enter A/B/C/D: ").strip().upper()
                
                user_answers.append(ans)

           
            print("________All answers recorded!__________")
            
            
            #  Hand off to review_agent via state transition 
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="quiz Completd. Answers collected",
                            tool_call_id = tool_call_id,
                        )
                    ],
                    "current_step": "review_agent",
                    "user_query":user_query,
                    "questions": output.questions, # [q.model_dump() for q in output.questions]
                    "user_answers": user_answers,

                    # "concept":      concept,
                    # "level":        level,
                    
                }
            )
    
    # except Exception as e:
    #     log_error("quiz_agent.py", "quiz_agent", str(e))
    #     raise CustomAppException(
    #         message=f"Quiz Agent error: {str(e)}",
    #         code=ErrorCode.INTERNAL_SERVER_ERROR,
    #         status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
    #     )
