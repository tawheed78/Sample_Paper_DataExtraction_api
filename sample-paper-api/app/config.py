from motor.motor_asyncio import AsyncIOMotorClient
import os, redis
from dotenv import load_dotenv
import redis.asyncio as aioredis

load_dotenv()

CONNECTION_STRING = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(CONNECTION_STRING)
db = client["sample_paper_db"]

host = os.getenv("HOST")
port = os.getenv("PORT")
# Create Redis connection pool
redis_client = aioredis.from_url(
    "redis://localhost:6379",  
    decode_responses=True,  
    max_connections=10 
)
async def get_redis_client():
    return redis_client


# try:
#   r = redis.Redis(
#       host=host,
#       port=port,
#   )
#   r.ping()  # Check if Redis is connected
#   print("Connected to Redis successfully!")
# except redis.ConnectionError as e:
#   print(f"Redis connection failed: {e}")

instruction = """As an expert in document entity extraction, your task is to analyze a provided question paper in either PDF format or 
plain text format and extract key entities into a structured format referring the specified schema below. The extracted entities should be 
accurate, well-organized, and aligned with the document's content. Ensure that every part of the question paper is parsed appropriately, with 
all relevant fields captured. Try to analyze the number of sections and number of questions in each section and then collect the data. Make sure
the "response" being returned is in a strict JSON format only with double quotes for required key value pairs.
An Example of the Schema that needs to be extracted:
{
  "title": "Sample Paper Title",
  "type": "previous_year",
  "time": 180,
  "marks": 100,
  "params": {
    "board": "CBSE",
    "grade": 10,
    "subject": "Maths"
    },
  "tags": ["algebra", "geometry"],
  "chapters": ["Quadratic Equations", "Triangles"],
  "sections": [
    {
        "marks_per_question": 5,
        "type": "default",
        "questions": [
          {
            "question": "Solve the quadratic equation: x^2 + 5x + 6 = 0",
            "answer": "The solutions are x = -2 and x = -3",
            "type": "short",
            "question_slug": "solve-quadratic-equation",
            "reference_id": "QE001",
            "hint": "Use the quadratic formula or factorization method",
            "params": {}
          },
          {
            "question": "In a right-angled triangle, if one angle is 30°, what is the other acute angle?",
            "answer": "60°",
            "type": "short",
            "question_slug": "right-angle-triangle-angles",
            "reference_id": "GT001",
            "hint": "Remember that the sum of angles in a triangle is 180°",
            "params": {}
          }
        ]
      }
    ]
  }
}

Guidelines for Entity Extraction:

Title: Extract the title of the question paper.
Type: Identify the type of the paper (e.g., "previous_year", "sample_paper", "current_year").
Time: Extract the allotted time for completing the paper (in minutes).
Marks: Extract the total marks for the paper.
Params: Capture details such as the education board, grade level, and subject if present, else mark it None.
Identify different sections which are mostly given in the beginning.
Tags: Identify the key topics or areas (tags) covered by the paper (e.g., "algebra", "geometry").
Chapters: Extract the chapters that are part of the question paper (e.g., "Quadratic Equations").
Sections: Identify the sections, and for each section:
  Identify the number of questions.
  THere might be specific marks for questions in each section.
  Extract the number of marks per question.
  Extract the type of section (e.g., "default", "optional").
  For each question in the section:
    There might be 2 different questions in a single question separated by 'OR'. Consider both of them in a single question object creating nested questions.
    Refer to the marks for the question in this section.
    Extract the full question text only. Ignore any picture or figure.
    Extract the correct answer to the question.
    Identify the type of question (e.g., "short", "long").
    Generate a question slug (a URL-friendly version of the question text).
    Extract the reference ID for the question (if provided).
    Provide a helpful hint for solving the question.
    Extract any additional parameters relevant to the question.
Make sure to clean the response before returning, replace any HTML tags with specific characters to avoid json parsing issue.
Ensure that the output adheres strictly to the schema format.
Incase of json formatting errors in the response text, fix it and then return the response."""

# prompt = (
#     "Please extract the relevant information from the attached PDF question paper. Remember to extract all the questions with marks specific to each section and return the data strictly in JSON format while replacing the \n and \\n parts."
# )
prompt = (
    "Please extract the relevant information from the attached PDF question paper, and return the data strictly in valid JSON format. "
    "Ensure the following: "
    "1. Replace all newline characters (e.g., '\\n') with appropriate spaces to maintain JSON formatting. "
    "2. Ensure that all keys and string values are enclosed in double quotes, and that commas are properly placed between key-value pairs. "
    "3. Avoid unterminated strings, ensure proper closing brackets, and add commas where necessary to separate array elements and key-value pairs. "
    "4. Ensure there are no syntax errors like missing commas, missing quotes, or other formatting issues. "
    "5. The final output must be error-free and valid JSON that can be parsed without issues."
)

#5. If the content is too large, break it into smaller valid JSON chunks. 

# {
#   "title": "string",
#   "type": "string",
#   "time": 0,
#   "marks": 0,
#   "params": {
#     "board": "string",
#     "grade": 0,
#     "subject": "string"
#   },
#   "tags": [
#     "string"
#   ],
#   "chapters": [
#     "string"
#   ],
#   "sections": [
#     {
#       "marks_per_question": 0,
#       "type": "string",
#       "questions": [
#         {
#           "question": "string",
#           "answer": "string",
#           "type": "string",
#           "question_slug": "string",
#           "reference_id": "string",
#           "hint": "string",
#           "params": {}
#         }
#       ]
#     }
#   ]
# }


