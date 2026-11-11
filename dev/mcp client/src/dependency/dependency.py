

from fastapi import Depends
from agents.main_prompt import MainSystemPrompt
from services.agent_service import AgentService
from agents.main_agent import MainAgent
from utils.gaurdrils import GuardrilsService
from utils.llm_client import Llm
from utils.bedrock_client import Bedrock
from utils.gaurdrils import GuardrilsService

def get_bedrock():
    return Bedrock()


def get_llm(bedrock: Bedrock = Depends(get_bedrock)):
    return Llm(bedrock)


def get_main_prompt():
    return MainSystemPrompt()

def get_main_agent(
        llm: Llm = Depends(get_llm),
        prompt: MainSystemPrompt = Depends(get_main_prompt)):
    return MainAgent(llm=llm, prompt=prompt)

def get_guardrils(
        llm: Llm = Depends(get_llm)
):
    return GuardrilsService(llm = llm)

def get_agent_service(
    agent: MainAgent = Depends(get_main_agent),
    guardrils: GuardrilsService = Depends(get_guardrils)
):
    return AgentService(agent=agent ,guardrils =guardrils)