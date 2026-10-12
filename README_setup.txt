Agentic AI project setup

1. Create a virtual environment:
   python -m venv .venv

2. Activate it on Windows PowerShell:
   .\.venv\Scripts\Activate.ps1

   Or on Windows Command Prompt:
   .venv\Scripts\activate.bat

3. Install dependencies:
   python -m pip install -r requirements.txt

4. Copy .env.example to .env and add your actual API keys/settings.
   Never commit .env or share real API keys.

Note: .venv is created locally by the command above; it is not a dependency
and should not be distributed in the project files.
