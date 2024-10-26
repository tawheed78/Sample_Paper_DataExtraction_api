﻿# Sample Paper API

## Overview
The **Sample Paper API** is a fast, scalable solution for performing CRUD operations with Sample papers along with extracting content from PDF files and Plain Text in a specified schema and saving the results to a database. This project is built using FastAPI, MongoDB, Redis for caching and integrates GeminiAI services to generate sample papers based on the extracted content. Background tasks are utilized to handle long-running PDF processing asynchronously, allowing users to check the status of their tasks via API.

## Features
- **CRUD Operations**: Create, Update, Retrieve or Delete a Sample Paper.
- **PDF File Extraction**: Upload PDF files to be processed asynchronously and extract relevant information.
- **Plain Text Extraction**: Upload Plain Text to be processed synchronously and extract relevant information.
- **Background Task Handling**: Long-running PDF extraction tasks are handled in the background, improving API responsiveness.
- **Task Status Checking**: Users can check the status of their PDF extraction tasks using the provided task ID.
- **Error Handling**: Graceful error handling for common issues, such as file format validation, database errors, and task failures.
- **Rate Limiting**: Prevents abuse by limiting the number of PDF uploads per minute.
- **API Documentation**: Interactive API documentation is provided via Swagger UI and Redoc.

---

## Table of Contents
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Technologies Used](#technologies-used)
- [Environment Variables](#environment-variables)
- [How It Works](#how-it-works)
- [Rate Limiting](#rate-limiting)
---

## Installation

### Prerequisites
Before you begin, ensure you have the following installed:
- **Python 3.8+**
- **MongoDB** (for storing task and extraction information)
- **Redis** (for caching frequently accessed data and storing Rate Limiting Counter)

### 1. Clone the Repository and create a virtual environment
```bash
git clone https://github.com/yourusername/Sample_Paper_DataExtraction_api.git
python -m venv venv
venv\Scripts\activate
cd sample-paper-api
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Create a .env file in the root directory with the following content
#### Add the localhost string on MongoDB and a Google API Key for Gemini. (https://aistudio.google.com/app/apikey)
#### You need a google cloud account for that.
```bash
MONGO_URI
GEMINI_API_KEY
```
### 4. Start the Backend Server and spin a Redis server locally.
```bash
uvicorn app.main:app --reload
redis-server (localhost)
```
### The Swagger UI docs will be accessible at http://127.0.0.1:8000/docs for testing.


## API Endpoints
### Create Sample Paper
#### Creates a new sample paper from JSON input. Returns the created paper's ID.
#### Request
```bash
POST /papers
```
### GET /papers/{paper_id}
#### Retrieves a sample paper by ID. Returns the JSON representation.
#### Request
```bash
GET /papers{paper_id}
```
### PUT /papers/{paper_id}
#### Updates an existing sample paper
#### Request
```bash
PUT /papers{paper_id}
```
### DELETE /papers/{paper_id}
#### Deletes a Sample Paper
#### Request
```bash
DELETE /papers{paper_id}
```
### POST /extract/pdf
#### Accepts a PDF file upload. Uses Gemini to extract information and convert it to the sample paper JSON format.
#### Request
```bash
POST /extract/pdf
```
### POST /extract/text
#### Accepts plain text input. Uses Gemini to extract information and convert it to the sample paper JSON format.
#### Request
```bash
POST /extract/text
```
### GET /tasks/{task_id}
#### Checks the status of a PDF extraction task.

```bash
GET tasks/{task_id}
```

## Technologies Used
- **FastAPI**: Python web framework for building APIs.
- **MongoDB**: NoSQL database used for storing task and extraction status.
- **Redis**: Caching frequently accessed papers and storing the Rate Limit Count.
- **GeminiAI**: Used to generate sample papers based on extracted PDF content and plain text input.
- **aiofiles**: For asynchronous file handling.
- **Pydantic**: Data validation and serialization.
- **Swagger UI**: Interactive API documentation.

## How It Works
### CRUD Operations for Papers

### Creating a Paper
Endpoint: POST /api/papers/
Users submit a request containing the paper details with all the required fields. (e.g., title, subject, total marks, time duration).
The system validates the input and creates a new paper in the database.
The response includes the newly created paper’s ID.

### Retrieving a Paper
Endpoint: GET papers/{paper_id}
Users can retrieve a paper stored in the database with the paper ID.

### Updating a Paper
Endpoint: PUT papers/{paper_id}/
Users can update an existing paper by submitting new details (e.g., changing title, time limit).
The system updates the paper details in the database and returns a success response.

### Deleting a Paper
Endpoint: DELETE papers/{paper_id}/
Users can delete a specific paper by its ID.
The system marks the paper for deletion, and it is removed from the database.

### PDF Upload & Task Initialization
Endpoint: POST /extract/pdf
The file is saved asynchronously to a directory, and a task is created in the MongoDB collection with a status of "In Progress".
A background task is initiated to extract the PDF content using Gemini API and the sample paper is saved to db after validating the response.

#### Background Task Processing
The background task (pdf_extraction_background_task) uploads the file to Gemini, generates a response, and attempts to save the sample paper to the database.
If the task is successful, the status is updated to "Completed", otherwise, it is marked as "Failed".

### Plain Text Upload
Endpoint: POST /extract/text
Plain text is passed as an input and the data is extracted from the text content using Gemini API and the sample paper is saved to db after validating the response.
It might throw an error just by clicking the execute command with the code 422. That is because of extra punctuation marks within the input which separates the content as a json response is required to be sent. Kindly remove any of those punctuation and newlines and proceed.
Working to enhance this feature by calling an API of any text beautifier to help with this.

### Task Status Check
Endpoint: GET /tasks/{task_id}
Users can poll the task status by hitting the above endpoint with the task ID provided in the PDF Upload task. The status field will be updated based on the progress of the background task.


## Rate Limiting
- The API's are rate-limited to specific number of requests per minute.
- This helps prevent excessive resource usage and ensures fair API usage.
- On exceeding the req/min limit, it throws an Error 429 - Too many requests.
