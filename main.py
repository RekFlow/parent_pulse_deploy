import json
import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "API key not found. Please set the OPENAI_API_KEY environment variable."
    )
os.environ["OPENAI_API_KEY"] = api_key

# Set up paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
calendar_path = os.path.join(BASE_DIR, "documents", "school_calendar.json")
grades_path = os.path.join(BASE_DIR, "documents", "science_grades.json")

# Load data
with open(calendar_path, "r") as f:
    calendar_data = json.load(f)
with open(grades_path, "r") as f:
    science_grades = json.load(f)

# Initialize embeddings and vector stores
embeddings = OpenAIEmbeddings()
grade_vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings,
    collection_name="grades",
)
event_vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings,
    collection_name="events",
)


def setup_grade_store():
    grade_collection = grade_vector_store.get()
    if len(grade_collection["ids"]) == 0:
        grade_documents = []

        # Add assignment documents
        for category, assignments in science_grades["categories"].items():
            for assignment in assignments:
                content = (
                    f"Category: {category}\n"
                    f"Assignment: {assignment.get('assignment', 'N/A')}\n"
                    f"Points: {assignment.get('points', 'N/A')}/{assignment.get('max', 'N/A')}\n"
                    f"Average: {assignment.get('average', 'N/A')}\n"
                    f"Status: {assignment.get('status', 'N/A')}\n"
                    f"Due Date: {assignment.get('due', 'N/A')}"
                )

                metadata = {
                    "subject": science_grades.get("subject", "N/A"),
                    "teacher": science_grades.get("teacher", "N/A"),
                    "student_name": science_grades["student"].get("name", "N/A"),
                    "student_year": science_grades["student"].get("year", "N/A"),
                    "category": category,
                }

                doc = Document(page_content=content, metadata=metadata)
                grade_documents.append(doc)

        # Add term grade document
        term_grade = science_grades.get("termGrade", "N/A")
        term_grade_doc = Document(
            page_content=f"Term Grade: {term_grade}",
            metadata={
                "subject": science_grades.get("subject", "N/A"),
                "teacher": science_grades.get("teacher", "N/A"),
                "student_name": science_grades["student"].get("name", "N/A"),
                "student_year": science_grades["student"].get("year", "N/A"),
                "category": "termGrade",
            },
        )
        grade_documents.append(term_grade_doc)
        grade_vector_store.add_documents(grade_documents)


def setup_event_store():
    event_collection = event_vector_store.get()
    if len(event_collection["ids"]) == 0:
        event_documents = []
        for event in calendar_data["events"]:
            event_date = event.get("date") or event.get(
                "date_range", "No date specified"
            )
            content = f"Date: {event_date}\nEvent: {event['event']}"
            metadata = {
                "calendar_year": calendar_data["calendar_year"],
                "date": event_date,
            }
            doc = Document(page_content=content, metadata=metadata)
            event_documents.append(doc)
        event_vector_store.add_documents(event_documents)


def query_grades(query_text):
    llm = ChatOpenAI(temperature=0)
    qa_prompt = PromptTemplate(
        template="""Answer the following question about student grades based on the provided context:
        
        Context: {context}
        Question: {question}
        
        Answer: """,
        input_variables=["context", "question"],
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=grade_vector_store.as_retriever(search_kwargs={"k": 10}),
        chain_type_kwargs={"prompt": qa_prompt},
    )

    result = qa_chain.invoke(query_text)
    return result["result"] if isinstance(result, dict) else result


def query_events(query_text, include_date=True):
    llm = ChatOpenAI(temperature=0)
    qa_prompt = PromptTemplate(
        template="""Answer the following question about school events based on the provided context:
        
        Context: {context}
        Question: {question}
        
        Answer: """,
        input_variables=["context", "question"],
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=event_vector_store.as_retriever(search_kwargs={"k": 10}),
        chain_type_kwargs={"prompt": qa_prompt},
    )

    if include_date:
        current_date = datetime.now().strftime("%Y-%m-%d")
        query_text = f"Current date is {current_date}. {query_text}"

    result = qa_chain.invoke(query_text)
    return result["result"] if isinstance(result, dict) else result


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print(json.dumps({"error": "Please provide query_type and query text"}))
        sys.exit(1)

    query_type = sys.argv[1]
    query = sys.argv[2]

    try:
        # Initialize stores if needed
        setup_grade_store()
        setup_event_store()

        if query_type == "grades":
            result = query_grades(query)
            print(json.dumps({"response": result}))
        elif query_type == "pastEvents":
            result = query_events(query, include_date=False)
            print(json.dumps({"response": result}))
        elif query_type == "upcomingEvents":
            result = query_events(query, include_date=True)
            print(json.dumps({"response": result}))
        else:
            print(json.dumps({"error": "Invalid query type"}))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
