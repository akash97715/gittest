from langchain.llms.base import LLM
from pydantic import BaseModel, Field
from typing import List, Optional, Mapping, Any
import logging

class IASOpenaiConversationalLLM(LLM, BaseModel):
    """Wrapper for IAS secured OpenAI chat API"""

    engine: str
    temperature: float
    max_tokens: int
    total_consumed_token: List[int] = Field(default_factory=list)
    system_message: Optional[str] = None
    client_id: Optional[str] = None
    x_vsl_client_id: Optional[str] = None
    bearer_auth: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "IAS_OpenAI"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
    ) -> str:
        prompt_message = prompt

        logging.debug(f"Prompt before adding system message: {prompt_message}")
        logging.debug(f"System message: {self.system_message} (Type: {type(self.system_message)})")

        # Ensure system_message is a string
        if self.system_message:
            if not isinstance(self.system_message, str):
                raise ValueError(f"Expected system_message to be a str, but got {type(self.system_message)}")
            prompt_message += " " + self.system_message  # Ensure system_message is a string

        logging.debug(f"Prompt after adding system message: {prompt_message}")

        token_consumed = self.get_num_tokens(prompt_message)
        logging.debug(f"Tokens consumed for prompt: {token_consumed}")

        response, totaltok = ias_openai_chat_completion(
            prompt_message,
            self.engine,
            self.temperature,
            calculate_max_tokens(self.max_tokens, str(self.engine), token_consumed),
            self.system_message,
            self.client_id,
            self.x_vsl_client_id,
        )

        logging.debug(f"Response from ias_openai_chat_completion: {response}")
        logging.debug(f"Total tokens received: {totaltok}")

        self.total_consumed_token.append(totaltok)
        logging.debug(f"Total consumed tokens list: {self.total_consumed_token}")

        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        params = {
            "engine": self.engine,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "total_consumed_token": self.total_consumed_token
        }
        return params

    def get_num_tokens(self, text: str) -> int:
        """Mock method to get number of tokens. Implement accordingly."""
        logging.debug(f"Getting number of tokens for text: {text}")
        return len(text.split())

def ias_openai_chat_completion(prompt, engine, temperature, max_tokens, system_message, client_id, x_vsl_client_id):
    """Mock function to simulate the OpenAI chat completion API call. Implement accordingly."""
    logging.debug(f"Calling ias_openai_chat_completion with prompt: {prompt}")
    # Simulate a response and token consumption
    response = f"Processed: {prompt}"
    totaltok = len(prompt.split())
    return response, totaltok

def calculate_max_tokens(max_tokens, engine, token_consumed):
    """Mock function to calculate the maximum number of tokens. Implement accordingly."""
    logging.debug(f"Calculating max tokens with max_tokens: {max_tokens}, engine: {engine}, token_consumed: {token_consumed}")
    return max_tokens - token_consumed

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    llm_engine = "gpt-3"  # Example engine name
    llm_config = {
        "engine": "text-davinci-003",
        "client_id": "example_client_id",
        "temperature": 0.7,
        "max_tokens": 100,
        "system_message": "Example system message"
    }

    # Choose the correct LLM class
    llm_class = (
        IASOpenaiConversationalLLM
        if llm_engine.startswith("gpt")
        else IASBedrockLLM  # Assuming IASBedrockLLM is defined elsewhere
    )

    # Initialize the LLM instance
    llm_instance = llm_class(**llm_config)

    # Create the QA chain
    qa = IAS_ConversationalRetrievalChain.from_llm(
        llm_instance,
        chain_type="stuff",
        retriever="vector_db",  # Assuming vector_db is defined elsewhere
        return_source_documents=True,
        max_tokens_limit=calculate_max_tokens(
            100, str(llm_engine), 10  # Example values for max_tokens and min_response_token
        ),
        response_if_no_docs_found="No documents found",  # Example response
        llm_response_flag=True,
        answer_from_llm_if_no_docs_found=True,
    )

    # Prepare the chat history
    chat_history = [{"user": "Hello", "bot": "Hi there!"}]  # Example chat history

    # Set the user query
    user_query = "What is the weather today?"

    # Execute the QA chain
    llm_response = qa(
        {
            "question": user_query,
            "chat_history": chat_history,
            "answer_with_llm_knowledge": "Answer from your own knowledge base if you don't know."
        }
    )

    # Print the response and total consumed tokens
    print(f"LLM Response: {llm_response}")
    print(f"Total consumed tokens: {llm_instance.total_consumed_token}")
