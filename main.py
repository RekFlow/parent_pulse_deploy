import json
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "API key not found. Please set the OPENAI_API_KEY environment variable."
    )

# Use the API key
os.environ["OPENAI_API_KEY"] = api_key

# import pandas as pd
from datetime import date, datetime

# First, load the source data from JSON files
with open("documents/school_calendar.json", "r") as f:
    calendar_data = json.load(f)

with open("documents/science_grades.json", "r") as f:
    science_grades = json.load(f)

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Langchain imports
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Access the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "API key not found. Please set the OPENAI_API_KEY environment variable."
    )

# Use the API key
os.environ["OPENAI_API_KEY"] = api_key

# Set up the vector database infrastructure
persist_directory = "chroma_db"

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Create two separate vector stores: one for events, one for grades
event_vector_store = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings,
    collection_name="events",
)
grade_vector_store = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings,
    collection_name="grades",
)

# Check if collections exist and have documents
event_collection = event_vector_store.get()
grade_collection = grade_vector_store.get()

# Add this inspection code
print("\nInspecting Grade Collection Contents:")
if grade_collection["ids"]:
    print(f"Number of documents: {len(grade_collection['ids'])}")
    print("\nDocument Contents:")
    for i, (doc_id, content, metadata) in enumerate(
        zip(
            grade_collection["ids"],
            grade_collection["documents"],
            grade_collection["metadatas"],
        )
    ):
        print(f"\nDocument {i+1}:")
        print(f"ID: {doc_id}")
        print(f"Content: {content}")
        print(f"Metadata: {metadata}")
else:
    print("Grade collection is empty")

# If events collection is empty, populate it
if len(event_collection["ids"]) == 0:
    # Transform calendar events into a format suitable for the vector store
    event_documents = []
    for event in calendar_data["events"]:
        event_date = event.get("date") or event.get("date_range", "No date specified")
        content = f"Date: {event_date}\nEvent: {event['event']}"
        metadata = {"calendar_year": calendar_data["calendar_year"], "date": event_date}
        doc = Document(page_content=content, metadata=metadata)
        event_documents.append(doc)

    # Add event documents to the vector store
    event_vector_store.add_documents(event_documents)
    print("Event documents added to the vector store")

# If grades collection is empty, populate it
"""
Populates the grade vector store if it's empty.

This code block:
1. Checks if the grade collection is empty
2. If empty, transforms grade data from science_grades into Document objects
3. For each assignment in each category:
   - Creates formatted content string with assignment details
   - Creates metadata dictionary with student and assignment info
   - Creates Document object and adds to grade_documents list
4. Documents include:
   - Category, assignment name, points, average, status and due date in content
   - Subject, teacher, student info, category and due date in metadata

The Document objects are later added to the grade vector store for similarity search.
"""
if len(grade_collection["ids"]) == 0:
    # Transform grade data into a format suitable for the vector store
    grade_documents = []
    for category, assignments in science_grades["categories"].items():
        for assignment in assignments:
            # Add debug print to verify data
            print(f"\nOriginal assignment data:")
            print(json.dumps(assignment, indent=2))

            content = f"Category: {category}\n"
            content += f"Assignment: {assignment.get('assignment', 'N/A')}\n"
            content += f"Points: {assignment.get('points', 'N/A')}/{assignment.get('max', 'N/A')}\n"
            content += f"Average: {assignment.get('average', 'N/A')}\n"
            content += f"Status: {assignment.get('status', 'N/A')}\n"
            content += f"Due Date: {assignment.get('due', 'N/A')}\n"

            # Verify the content is complete
            print("\nVerifying document content:")
            print(content)

            metadata = {
                "subject": science_grades.get("subject", "N/A"),
                "teacher": science_grades.get("teacher", "N/A"),
                "student_name": science_grades["student"].get("name", "N/A"),
                "student_year": science_grades["student"].get("year", "N/A"),
                "category": category,
                "assignment": assignment.get("assignment", "N/A"),
                "points": assignment.get("points", "N/A"),
                "max": assignment.get("max", "N/A"),
                "average": assignment.get("average", "N/A"),
                "status": assignment.get("status", "N/A"),
                "due_date": assignment.get("due", "N/A"),
            }
            doc = Document(page_content=content, metadata=metadata)
            grade_documents.append(doc)

    # Add term grade as a document
    term_grade = science_grades.get("termGrade", "N/A")
    term_grade_content = f"Term Grade: {term_grade}"
    term_grade_metadata = {
        "subject": science_grades.get("subject", "N/A"),
        "teacher": science_grades.get("teacher", "N/A"),
        "student_name": science_grades["student"].get("name", "N/A"),
        "student_year": science_grades["student"].get("year", "N/A"),
        "category": "termGrade",
    }
    term_grade_doc = Document(
        page_content=term_grade_content, metadata=term_grade_metadata
    )
    grade_documents.append(term_grade_doc)

    # Verify documents before adding to store
    print("\nVerifying all documents before storage:")
    for doc in grade_documents:
        print("\n---")
        print(doc.page_content)

    grade_vector_store.add_documents(grade_documents)
    print("Grade documents added to the vector store")

# Set up the QA system with GPT-4
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
# If you don't know the answer, just say "I don't know
# Define a more specific prompt template for the QA chain
qa_prompt_template = """You are an AI assistant tasked with answering questions about school events and student grades. Use the provided context to ensure accurate and helpful responses.

# Steps

1. **Understand the Context**: Carefully review the provided context about school events and student grades.
2. **Identify the Question**: Determine what specific information or answer the question is seeking.
3. **Locate Relevant Information**: Use the context to find details relevant to the question, focusing on key terms and data.
4. **Formulate the Answer**: Compose a clear, concise, and accurate answer based on the context provided.
5. **Review and Refine**: Ensure the answer directly addresses the question and is free from errors.

# Output Format

Provide a concise paragraph that directly responds to the question with relevant information from the context.

# Examples

**Input**: "What is the date for the next school event?"
**Context**: "The next school dance is scheduled for April 10th. Student grades will be released on April 14th."
**Output**: "The next school event, the school dance, is scheduled for April 10th."

**Input**: "When will student grades be available?"
**Context**: "The next school dance is scheduled for April 10th. Student grades will be released on April 14th."
**Output**: "Student grades will be available on April 14th."

# Notes

- Ensure the answer is derived solely from the provided context.
- If the context lacks the necessary information to answer a question, indicate that the information is not available. ".

Context: {context}

Question: {question}

Answer: """

qa_prompt = PromptTemplate(
    template=qa_prompt_template, input_variables=["context", "question"]
)

# Create two QA chains: one for events, one for grades
event_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    # The retriever is used to fetch relevant documents from the event vector store based on the input query.
    # This is necessary to provide context for the language model to generate accurate answers.
    # The `as_retriever` method converts the `event_vector_store` object into a retriever.
    # This retriever is used to fetch relevant documents from the event vector store based on the input query.
    retriever=event_vector_store.as_retriever(search_kwargs={"k": 10}),
    chain_type_kwargs={"prompt": qa_prompt},
)

grade_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=grade_vector_store.as_retriever(search_kwargs={"k": 10}),
    chain_type_kwargs={"prompt": qa_prompt},
)


# Query function for events - can include current date context if needed
def query_data_events(query, include_date=True):
    print(f"Input query: {query}")

    if include_date:
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Append current date to the query
        augmented_query = f"Current date is {current_date}. {query}"
    else:
        augmented_query = query

    event_docs = event_vector_store.similarity_search(augmented_query)
    print(f"Retrieved event documents: {event_docs}")

    event_result = event_qa.invoke(augmented_query)
    print(f"Event result: {event_result}")

    return f"Events: {event_result}"


# Query function for grades
def query_data_grades(query):
    print(f"Input query: {query}")

    # Get the documents from the vector store
    grade_docs = grade_vector_store.similarity_search(query, k=20)

    # Create a context string that includes ALL the document content
    context = ""
    for doc in grade_docs:
        # Print full document for debugging
        print(f"\nRetrieved document content:")
        print(doc.page_content)  # This should now show all fields
        print(f"Document metadata: {doc.metadata}")

        # Add to context with clear separation
        context += f"\n---\n{doc.page_content}"

    grade_result = grade_qa.invoke(
        {"query": query, "context": "\n".join([doc.page_content for doc in grade_docs])}
    )
    print(f"Grade result: {grade_result}")

    return f"Grades: {grade_result}"


# Interactive terminal interface
while True:
    print("\nSchool Information System")
    print("1. Query Past Events")
    print("2. Query Grades")
    print("3. Query Upcoming Events")
    print("4. Exit")

    choice = input("\nEnter your choice (1-4): ")

    if choice == "1":
        query = input("Enter your event query: ")
        result = query_data_events(query)
        print(result)

    elif choice == "2":
        query = input("Enter your grade query: ")
        result = query_data_grades(query)
        print(result)

    elif choice == "3":
        query = input("Enter your upcoming events query: ")
        result = query_data_events(query, include_date=True)
        print(result)

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid choice. Please try again.")
