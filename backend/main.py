from openai import OpenAI
from langfuse.openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from langfuse.decorators import observe, langfuse_context
from utils.logger_utils import setup_logger
import logging

load_dotenv()

from langfuse import Langfuse

# Initialize Langfuse client
langfuse = Langfuse()


class QueryRequest(BaseModel):
    query: str
    max_new_tokens: int = 1024


app = FastAPI()
openai = OpenAI()
LOGGER_NAME = "BACKEND_LOGGER"
setup_logger(LOGGER_NAME)
logger = logging.getLogger(LOGGER_NAME)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@observe()
async def generate_stream(query: str, max_new_tokens: int = 1024):
    """
    Generate a streaming response from OpenAI, handling completion correctly.

    Args:
        query (str): The user's query
        max_new_tokens (int): Maximum number of tokens to generate

    Yields:
        str: Chunks of the generated response
    """
    try:
        # Get production prompt
        prompt = langfuse.get_prompt("other-test-prompt")
        # variable names can only be alpha + underscores
        new_prompt = prompt.compile(var_one="Laila", var_two="Welcome")
        # Can be used as alternative to the langfuse openai sdk + the parameter langfuse_prompt
        #langfuse_context.update_current_observation(prompt=prompt,)
        logger.info(new_prompt)
        stream = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": new_prompt + query,
                },
            ],
            stream=True,
            max_tokens=max_new_tokens,
            langfuse_prompt=prompt
        )

        # Track the complete response to prevent repetition
        full_response = ""

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

            # Check if this is the last chunk (stream completion)
            if chunk.choices[0].finish_reason is not None:
                break

    except Exception as e:
        yield f"An error occurred: {str(e)}"


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/query-stream")
async def query_stream(request: QueryRequest):
    """
    Endpoint for streaming query responses

    Args:
        request (QueryRequest): Request containing query and max tokens

    Returns:
        StreamingResponse: A streaming response of the generated content
    """
    return StreamingResponse(
        generate_stream(request.query, max_new_tokens=request.max_new_tokens),
        media_type='text/event-stream'
    )
