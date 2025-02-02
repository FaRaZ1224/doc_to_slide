# Markdown Document Splitter

A Python tool that splits markdown documents into presentation-ready sections using GPT-4o-mini.

## Features
- Splits markdown documents into a specified number of sections (1-50)
- Preserves all original formatting and content
- Maintains logical section boundaries
- Ensures sections can be rejoined to match the original document

## Setup
1. Install requirements:   ```bash
   pip install -r requirements.txt   ```

2. Set your OpenAI API key:
   - Replace `"your-openai-api-key"` in `gpt.py` with your actual API key
   - Or use environment variables (recommended)

## Usage 
 
1. **Paste the document**  
2. **Press**:  
   - **Ctrl+D (Mac/Linux)**  
   - **Ctrl+Z (Windows)**  
   _(This signals EOF, letting the script know you're done entering text.)_  
3. **Enter the number of slides** (e.g., `3`)  
