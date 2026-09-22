from config.prompts import QUESTION_GENERATION_PROMPT, STUDY_GUIDE_PROMPT, SUMMARY_PROMPT
from src.logger import logger
from src.retriver import RetriverManager
from src.llm import LLMManager


class RAGpipeline:
    """Responsible for connecting the retriever, prompts, and LLM."""

    def __init__(self, vectorstore):
        logger.info("Initializing RAG pipeline")
        self.retriever = RetriverManager(vectorstore)
        self.llm = LLMManager()

    def _build_context(self, documents):
        if not documents:
            return ""
        return "\n\n".join(doc.page_content for doc in documents)

    def ask(self, question: str):
        logger.info(f"User question: {question}")
        documents = self.retriever.retrieve(question)
        context = self._build_context(documents)

        if not context:
            return {
                "answer": "I could not find relevant content in the uploaded document.",
                "context": "",
                "documents": documents,
            }

        answer = self.llm.generate_answer(context=context, question=question)
        logger.info("Answer generated successfully")

        return {
            "answer": answer,
            "context": context,
            "documents": documents,
        }

    def summarize_document(self, question: str):
        documents = self.retriever.retrieve(question)
        context = self._build_context(documents)
        prompt = SUMMARY_PROMPT.format(context=context, question=question)
        answer = self.llm.generate_from_prompt(prompt)
        return {"answer": answer, "context": context, "documents": documents}

    def create_study_guide(self, question: str):
        documents = self.retriever.retrieve(question)
        context = self._build_context(documents)
        prompt = STUDY_GUIDE_PROMPT.format(context=context, question=question)
        answer = self.llm.generate_from_prompt(prompt)
        return {"answer": answer, "context": context, "documents": documents}

    def generate_questions(self, question: str, count: int = 10):
        documents = self.retriever.retrieve(question)
        context = self._build_context(documents)
        prompt = QUESTION_GENERATION_PROMPT.format(context=context, question=f"{question} Generate {count} questions.")
        answer = self.llm.generate_from_prompt(prompt)
        return {"answer": answer, "context": context, "documents": documents}