
This repository explores basic functionalities of langfuse, specifically its prompt management and its tracing. 
It is an exploratory repository. 

The prompt being tested is exactly as follows: 
`hello, my name is {{var_one}}, I am testing adding a variable. Please say {{var_two}} !`

# Set up 
Create a conda environment and then run: 
```bash 
pip install -r requirements.txt
```

# Code
There is a frontend built in streamlit. The backend is a fastapi endpoint.

To run the frontend: 
```bash
cd frontend
streamlit run streamlit_app.py
```

To run backend: 
1. create .env file in directory `backend/` with the following variables set:
`OPENAI_API_KEY`, `LANGFUSE_SECRET_KEY`,`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST. 
2. run the following commands: 
```bash 
cd backend
uvicorn main:app --port 8000 --reload 
```
   