import httpx
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq

from config.settings import CHAT_MODEL, TEMPERATURE, GROQ_API_KEY, MISTRAL_API_KEY
from config.prompts import ANSWER_TEMPLATE, SYSTEM_PROMPT
from src.logger import logger


class LLMManager:
    """Responsible for initializing the active LLM provider and generating answers."""

    def __init__(self):
        if GROQ_API_KEY:
            logger.info("Initializing Groq LLM")
            self.llm = ChatGroq(
                model=CHAT_MODEL,
                temperature=TEMPERATURE,
                api_key=GROQ_API_KEY,
            )
        elif MISTRAL_API_KEY:
            logger.info("Initializing Mistral LLM")
            self.llm = ChatMistralAI(
                model=CHAT_MODEL,
                temperature=TEMPERATURE,
                api_key=MISTRAL_API_KEY,
            )
        else:
            raise ValueError(
                "No API key found. Please set GROQ_API_KEY or MISTRAL_API_KEY in your .env file."
            )

    def generate_from_prompt(self, prompt: str) -> str:
        logger.info("Sending prompt to LLM")
        try:
            response = self.llm.invoke(prompt)
            logger.info("LLM response generated")
            return response.content
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code == 429:
                message = "The AI service is currently rate-limited. Please wait a moment and try again."
            else:
                message = f"The AI service responded with an error (status {status_code}). Please try again later."
            logger.warning(message)
            raise ValueError(message) from exc
        except Exception as exc:
            logger.exception("LLM call failed")
            raise ValueError("The AI response could not be generated right now. Please try again.") from exc

    def generate_direct_answer(self, question: str) -> str:
        prompt = f"Answer the user question clearly and concisely.\n\nQuestion: {question}"
        return self.generate_from_prompt(prompt)

    def generate_from_prompt_stream(self, prompt: str):
        logger.info("Sending prompt to LLM in streaming mode")
        try:
            for chunk in self.llm.stream(prompt):
                content = getattr(chunk, "content", "")
                if content:
                    yield str(content)
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code == 429:
                raise ValueError("The AI service is currently rate-limited. Please wait a moment and try again.") from exc
            raise ValueError(f"The AI service responded with an error (status {status_code}). Please try again later.") from exc
        except Exception as exc:
            raise ValueError("The AI response could not be generated right now. Please try again.") from exc

    def generate_direct_answer_stream(self, question: str):
        prompt = f"Answer the user question clearly and concisely.\n\nQuestion: {question}"
        yield from self.generate_from_prompt_stream(prompt)

    def generate_answer(self, context: str, question: str) -> str:
        logger.info("Formatting RAG prompt")
        prompt = ANSWER_TEMPLATE.format(context=context, question=question)
        return self.generate_from_prompt(prompt)

    def generate_answer_stream(self, context: str, question: str):
        logger.info("Formatting RAG prompt for streaming")
        prompt = ANSWER_TEMPLATE.format(context=context, question=question)
        yield from self.generate_from_prompt_stream(prompt)