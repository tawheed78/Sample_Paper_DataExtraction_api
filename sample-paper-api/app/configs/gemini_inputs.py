safe= [
  {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_NONE",
  },
  {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_NONE",
  },
  {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_NONE",
  },
  {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_NONE",
  },
]

response_schema = {
  "title": "string",
  "type": "string",
  "time": int,
  "marks": int,
  "params": {},
  "tags": [
    "string"
  ],
  "chapters": [
    "string"
  ],
  "sections": [
    {
      "marks_per_question": int,
      "type": "string",
      "questions": [
        {
          "question": "string",
          "answer": {},
          "type": "string",
          "question_slug": "string",
          "reference_id": {},
          "hint": {},
          "params": {}
        }
      ]
    }
  ]
}

INSTRUCTION="""As an expert in document entity extraction, your task is to analyze a provided question paper in either PDF
format or plain text format and extract key entities into a structured format referring the specified schema below. The extracted entities should be
accurate, well-organized, and aligned with the document's content. Ensure that every part of the question paper is parsed appropriately, with
all relevant fields captured. Try to analyze the number of sections and number of questions in each section and then collect the data. Make sure
the "response" being returned is in a strict JSON format only with double quotes for required key value pairs.
An Example of the Response that needs to be returned referring to Response Schema:
{
  "title": "HINDUSTANI MUSIC Melodic Instrument",
  "type": "sample_paper",
  "time": 120,
  "marks": 30,
  "params": {
    "board": null,
    "grade": 10,
    "subject": "Hindustani Music"
  },
  "tags": [
    "Raga",
    "Taal",
    "Melodic Instruments"
  ],
  "chapters": [],
  "sections": [
    {
      "marks_per_question": 1,
      "type": "default",
      "questions": [
        {
          "question": "Name the taal :\n1 2 3 4 5 6 7\n0 2     Dhi Na\n  3\n1. Tilwada\n2. Teentaal\n3. Rupak\n4. Dadra",
          "answer": "2",
          "type": "mcq",
          "question_slug": "name-the-taal",
          "reference_id": null,
          "hint": null,
          "params": {}
        },
        {
          "question": "Choose the correct statements :\nA. Komal Rishab is used in raga Bhupali\nB. Jati of Brindavani Sarang is Shadav Shadav\nC. Jati of Bhupali is Audav Audav\nD. Komal Nishad is used in raga Khamaj\nChoose the correct option\n1. A & B\n2. B & C\n3. C & D\n4. A & D",
          "answer": "1",
          "type": "mcq",
          "question_slug": "choose-the-correct-statements",
          "reference_id": null,
          "hint": null,
          "params": {}
        },
        {
          "question": "Choose the correct statement\nA. Jati of Khamaj is Shadav Sampurna\nB. Tansen was court musician of Shahjahan\nC. Dadra Tal has two vibhag\nD. Aalap is played in slow speed\nChoose the correct option\n1. A, B & C\n2. A, C & D\n3. B, C & D\n4. A, B & D",
          "answer": "4",
          "type": "mcq",
          "question_slug": "choose-the-correct-statement",
          "reference_id": null,
          "hint": null,
          "params": {}
        },
        {
          "question": "Match List I with List II\nList I  List II\nA. Khamaj      I. dha Tirkit dhin dhin\nB. Tilwada    II. Sitar\nC. Dugun        III. SNDPMGRS\nD. Inayat Khan IV. RM PM\nChoose the correct answer from the options given below:\n1. A - IV, B - III, C - II, D - 1\n2. A-III, B-I, C-IV, D-II\n3. A-I, B-II, C-III, D-IV\n4. A-II, B-IV, C-I, D-III",
          "answer": "2",
          "type": "match",
          "question_slug": "match-list-i-with-list-ii",
          "reference_id": null,
          "hint": null,
          "params": {}
        }
      ]
    },
    {
      "marks_per_question": 2,
      "type": "default",
      "questions": [
        {
          "question": "Describe the salient features of Raga Bhupali.\n(OR)\nDefine Alaap and Taan with illustrations.",
          "answer": null,
          "type": "descriptive",
          "question_slug": "describe-the-salient-features-of-raga-bhupali",
          "reference_id": null,
          "hint": null,
          "params": {}
        },
        {
          "question": "Describe Dhrupad and its Vanis.\n(OR)\nDiscuss the Tuning of the instrument opted for.",
          "answer": null,
          "type": "descriptive",
          "question_slug": "describe-dhrupad-and-its-vanis",
          "reference_id": null,
          "hint": null,
          "params": {}
        },
        {
          "question": "Describe the salient features of Maseetkhani Gat.\n(OR)\nDescribe Tala Rupak and write its Dugun in Tala Notation System.",
          "answer": null,
          "type": "descriptive",
          "question_slug": "describe-the-salient-features-of-maseekhani-gat",
          "reference_id": null,
          "hint": null,
          "params": {}
        }
      ]
    },
    {
      "marks_per_question": 6,
      "type": "default",
      "questions": [
        {
          "question": "Write a Razakhani Gat in Raga Khamaj with two Tanas in notation system.\n(OR)\nDescribe Tilwada Tala and write its Tigun and Chaugun in Tala notation system.",
          "answer": null,
          "type": "descriptive",
          "question_slug": "write-a-razakhani-gat-in-raga-khamaj-with-two-tanas-in-notation-system",
          "reference_id": null,
          "hint": null,
          "params": {}
        },
        {
          "question": "Raga is the soul of Indian Classical Music every raga is unique and have its own distinct features. Some of the features of a Raga are Thaat, Aroh, Vadi, Time etc. Same raga is performed differently by different artistes depending upon their mood and learning. But essentially features of the raga remains the same. After reading the above paragraph, describe all the features of a raga with examples from three different ragas. \n(OR)\nCritically analyse the style of any one present day artist of melodic instrumental music.",
          "answer": null,
          "type": "descriptive",
          "question_slug": "raga-is-the-soul-of-indian-classical-music-every-raga-is-unique-and-have-its-own-distinct-features",
          "reference_id": null,
          "hint": null,
          "params": {}
        }
      ]
    }
  ]
}
Carefully learn the above schema and return response in the same format only.
Guidelines for Entity Extraction:
The question paper can be in different languages. Process it accordingly.
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
  There might be specific marks for questions in each section.
  Extract the number of marks per question.
  Extract the type of section (e.g., "default", "optional").
  Go through the sections strictly as they might be marked as 'A','B','C','D','E' and so on or 'I','II','III','IV','V' and so on.
  Every section needs to be captured. Chances are first section will always be a MCQ.
  Avoid duplicate key errors due to missing "{}" brackets or ',' delimiters.
  For each question in the section:
    There might be 2 different questions in a single question separated by 'OR'. Consider both of them in a single question object creating nested questions.
    Refer to the marks for the question in this section.
    Extract the full question text only. Ignore any picture or figure.
    Extract the correct answer to the question if it is an 'MCQ' else just put "Need to be solved.".
    Identify the type of question (e.g., "short", "long").
    Generate a question slug (a URL-friendly version of the question text of maximum 5 words only).
    Extract the reference ID for the question (if provided).
    Provide a helpful hint for solving the question.
    Extract any additional parameters relevant to the question.
Make sure to clean the response before returning, replace any HTML tags with specific characters to avoid json parsing issue.
Ensure that the output adheres strictly to the schema format.
Incase of json formatting errors in the response text, fix it and then return the response.
Finally please review the JSON response you provided. 
Ensure there are no missing commas and brackets, which are causing errors 
in validation like duplicate keys as the bracket are not closed. Specifically, the response should have properly closed objects and arrays.
"""

PROMPT ="""Please extract the relevant information from the attached PDF question paper, and return the 
    data strictly in valid JSON format.
    Ensure the following: "
    1. Replace all newline characters (e.g., '\\n') with appropriate spaces to maintain JSON 
      formatting.
    2. Ensure that all keys and string values are enclosed in double quotes, and that commas are 
      properly placed between key-value pairs.
    3. Ensure proper closing brackets, and add commas wherever necessary.
    4. Ensure there are no syntax errors like missing commas, missing quotes, brackets or other 
      formatting issues. 
    5. The final output must be error-free and a valid JSON that can be parsed without issues according to the Paper Model below.
    
    PaperModel:
    class ParamsModel(BaseModel):
    "Model representing parameters for a given board, subject and grade."
      board: Optional[str]= {}
      grade: int
      subject: str

    class QuestionsModel(BaseModel):
    "Model representing question with its attributes."
      question: str
      answer: Optional[str] = {}
      type: str
      question_slug: str
      reference_id: Optional[str] = {}
      hint: Optional[str] = {}
      params: Optional[Dict[str, Any]] = {}

class SectionModel(BaseModel):
    "Model representing Section and its attributes."
      marks_per_question: int
      type: str
      questions: List[QuestionsModel]

class PaperModel(BaseModel):
    "Model representing complete PaperModel with its attributes"
      title: str
      type: str
      time: int
      marks: int
      params: Optional[ParamsModel] = {}
      tags: List[str]
      chapters: List[str]
      sections: List[SectionModel]"""