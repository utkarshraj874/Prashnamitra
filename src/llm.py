from langchain_mistralai import ChatMistralAI

from config.settings import CHAT_MODEL,TEMPERATURE

from config.prompts import SYSTEM_PROMPT

from src.logger import logger 

class LLMManager:
    """
    responsible for intializing the LLM
    and generating answers using the rag prompt 
    
    """

    def __init__(self):
        logger.info("Initializing Mistral LLM")

        self.llm = ChatMistralAI(
            model = CHAT_MODEL,
            temperature = TEMPERATURE
        )

    def generate_answer(
                        self,
                        context: str,
                        question: str,) -> str:
        logger.info("Formatting RAG Prompt ")

        # prompt = SYSTEM_PROMPT.invoke({
        #     "context":context,
        #     "question":question,
        # })
         
        prompt = SYSTEM_PROMPT
        
        logger.info("Sending prompt to LLM ")

        response = self.llm.invoke(prompt)

        logger.info("LLM response Generated ")

        return response.content