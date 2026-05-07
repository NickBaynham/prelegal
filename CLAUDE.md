# PreLegal Project
## Overview
This is a SaaS project to allow users to draft legal agreements based on templates in the templates directory. The user can carry out a chat in order to establish which document they want to draft and to fill in the fields. The available document templates are cataloged in the catalog.json file in the root of the project:

@catalog.json

Before we start: The initial implementation is a frontend only prototype that only supports this mutual NDA document without AI chat. It simply provides the form to collect the required information to draft the NDA.

## Development Process
When instructed to build a feature:
1. Use your Atlassian tools to read the feature instructions from JIRA.
2. If the feature includes a definition of done or acceptance criteria, use that to first create the tests to verify the feature has been implemented successfully.
2. Develop the feature. Remember to always add the unit, integration and E2E tests first. Add any appropriate documentation for development and end-users.
3. Do not skip any step from the feature-dev 7 step process.
4. Thoroughly test the feature with unit, integration, and E2E tests and fix any issues.
5. Submit a PR using your github tools.

## AI Design
When writing code to make calls to an LLM, use your cerebras skill to use liteLLM via OpenRouter to the `openrouter/openai/gpt-oss-120b` model with cerebras as the inference provider. You should use structured outputs so that you can interpret the results and populate fields in the legal document. 

## Technical Design
The entire project should be packaged as a Docker container. The backend should be in backend/ and be the pdm project using FastAPI. The front end should be in frontend/ Consider staticaly building the frontend and serving it via FastAPI. Create scripts in scripts/ for:
```
# Mac
scripts/start-mac.sh # Start
scripts/stop-mac.sh  # Stop

# Linux
scripts/start-linux.sh 
scripts/stop-linux.sh

# Windows
scripts/start-windows.ps1
scripts/stop-windows.ps1

# Make
make docker-up
make docker-down
```
Wrap these commands in Make commands, and have make figure out the host OS and the appropriate script to call.

Backend available at http://localhost:8000

The backend database should use SQLLite as a starting point to persist all data.

## Color Scheme
- Accent Gold: #E9A93A
- Blue Primary: #2E9FD8
- Purple Secondary: #7B4EA3
- Dark Navy: #10233F
- Grey Text: #68707A
- Warm Paper: #F6F3EA
- Card White: #FFFFFF
- Route Green: #4F9F78
- Soft Border: #E4DED2
- Alert Amber: #F5B84B
- Critical Red: #D94A3A
- Success Green: #3E8F65