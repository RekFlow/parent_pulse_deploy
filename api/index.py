import json
import logging
import os
from xml.dom.minidom import Document

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from mangum import Mangum
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the data
with open("api/documents/science_grades.json", "r") as f:
    grades_data = json.load(f)

with open("api/documents/school_calendar.json", "r") as f:
    calendar_data = json.load(f)

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Initialize Chroma stores
grade_vector_store = Chroma(
    collection_name="grades",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

event_vector_store = Chroma(
    collection_name="events",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)


class Query(BaseModel):
    query_type: str
    query_text: str


def setup_grade_store():
    try:
        # Check if documents already exist
        if grade_vector_store.get()["ids"]:
            logger.info("Grade documents already loaded")
            return

        logger.info("Loading grade documents into Chroma")

        documents = []
        for category, assignments in grades_data["categories"].items():
            for assignment in assignments:
                content = f"{category} - {assignment['assignment']}: {assignment['points']}/{assignment['max']} ({assignment['average']}%)"
                documents.append(
                    Document(
                        page_content=content,
                        metadata={"category": category, "date": assignment["due"]},
                    )
                )

        logger.info(f"Adding {len(documents)} grades to Chroma")
        grade_vector_store.add_documents(documents)
        logger.info("Grades successfully loaded into Chroma")

    except Exception as e:
        logger.error(f"Error setting up grade store: {str(e)}")
        raise


def setup_event_store():
    try:
        # Check if documents already exist
        if event_vector_store.get()["ids"]:
            logger.info("Event documents already loaded")
            return

        logger.info("Loading event documents into Chroma")

        documents = []
        for event in calendar_data["events"]:
            # Create a detailed description for each event
            if "date" in event:
                content = f"On {event['date']}, {event['event']}"
            else:
                content = f"From {event['start_date']} to {event['end_date']}, {event['event']}"

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "date": event.get("date", event.get("start_date")),
                        "event_name": event["event"],
                    },
                )
            )

        logger.info(f"Adding {len(documents)} events to Chroma")
        event_vector_store.add_documents(documents)
        logger.info("Events successfully loaded into Chroma")

    except Exception as e:
        logger.error(f"Error setting up event store: {str(e)}")
        raise


def query_grades(query_text):
    try:
        template = """Answer the following question about grades based on the provided context.
        
        Context: {context}
        Question: {question}
        
        Answer:"""

        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0),
            chain_type="stuff",
            retriever=grade_vector_store.as_retriever(),
            chain_type_kwargs={"prompt": PromptTemplate.from_template(template)},
        )

        return qa_chain({"query": query_text})["result"]
    except Exception as e:
        logger.error(f"Error in query_grades: {str(e)}")
        return "Sorry, I couldn't process your question about grades."


def query_events(query_text, include_date=True):
    try:
        template = """Answer the following question about school events based on the provided context.
        
        Context: {context}
        Question: {question}
        
        Answer:"""

        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0),
            chain_type="stuff",
            retriever=event_vector_store.as_retriever(),
            chain_type_kwargs={"prompt": PromptTemplate.from_template(template)},
        )

        return qa_chain({"query": query_text})["result"]
    except Exception as e:
        logger.error(f"Error in query_events: {str(e)}")
        return "Sorry, I couldn't process your question about events."


@app.post("/api/query")
async def process_query(query_request: Query):
    try:
        setup_grade_store()
        setup_event_store()

        if query_request.query_type == "grades":
            result = query_grades(query_request.query_text)
        elif query_request.query_type in ["pastEvents", "upcomingEvents"]:
            result = query_events(query_request.query_text)
        else:
            raise HTTPException(status_code=400, detail="Invalid query type")

        return {"response": result}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Add this at the end for Vercel
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
