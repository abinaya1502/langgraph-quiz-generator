from typing import List, Literal, Optional
from pydantic import BaseModel

#  Shared 
class QuizAgentRequest(BaseModel):
    user_id: str
    user_query : str
    # concept: str
    # level: Optional [Literal["easy","medium","advance"]] = "medium"
    # no_of_questions: Optional[int] = 3  
    
    
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer : str


class QuizAgentResponse(BaseModel):
    thread_id: str
    # concept: str
    # no_of_questions:int
    questions: List[QuizQuestion]

class ReviewAgentRequest(BaseModel):
    user_id: str
    # concept: str
    # level: Literal["easy","medium","advance"] 
    questions: List[QuizQuestion]
    user_answers: List[str]

class WrongAnswerExplanation(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    explanation: str

class ReviewAgentResponse(BaseModel):
    correct_count : int
    wrong_count: int
    grade: str
    wrong_explanations: List[WrongAnswerExplanation]
    feedback: str
    thread_id: str

class GuardrilsResponse(BaseModel):
    continue_: bool
    message : Optional[str] = None