from src.logger import logger 
from src.retriver import RetriverManager
from src.llm import LLMManager

class RAGpipeline:
    """
    Responsible for connecting 
    retriever + Prompt + LLM
    """

    def __init__(self, vectorstore):

        logger.info("Initializing RAG pipeline ")

        self.retriever = RetriverManager(vectorstore)
        
        self.llm = LLMManager()

    def ask(self, question: str):

        logger.info(f"User question : {question}")

        #retriever relevent Documents
        documents = self.retriever.retrieve(question)


        #converting document into context 
        context = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        logger.info("Context Created ")

        #Generate final Answer
        answer = self.llm.generate_answer(
            context = context,
            question = question
        )

        logger.info("Answer Generated Succesfully ")

        return {
            "answer":answer,
            "context":context,
            "documents":documents
        }