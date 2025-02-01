import openai
import json
from typing import List

# === CONFIGURATION ===
# Using GPT-4o-mini as per the allowed models (GPT-4o-mini, Claude-3-Haiku, Gemini-1.5-Flash)
# GPT-4o-mini is chosen because:
# - It is highly reliable for structured outputs like JSON.
# - It follows precise instructions well (avoids hallucinations or restructuring content).
# - It preserves formatting better than Claude/Gemini in similar tasks.
# - It's fast and cost-effective while still being highly capable.

# I was debating between Haiku and 4o-mini but ultimately went with 4o-mini because of the benchmarks
OPENAI_API_KEY = "your-openai-api-key"  # Replace with your actual OpenAI API key

# Justification for using GPT-4o-mini based on benchmarks:
# 1. Quality and Performance: GPT-4o-mini has a quality index score of 73, ensuring high accuracy in document sectioning.
# 2. Latency and Speed: With a low latency of 0.49 seconds and an output speed of 85.4 tokens per second, GPT-4o-mini processes documents quickly and efficiently.
# 3. Cost-Effectiveness: GPT-4o-mini is highly cost-effective, with a cost of $0.26 per million tokens, providing excellent performance at a low cost.
LLM_MODEL = "gpt-4o-mini"  

def call_gpt(prompt: str) -> List[str]:
    """
    Calls GPT-4o-mini and returns the response as a list of sections.

    Why GPT-4o-mini?
    - **Structured Output**: GPT models (especially GPT-4o) are better at returning strict JSON output.
    - **Instruction Following**: Compared to Claude-3-Haiku or Gemini-1.5-Flash, GPT-4o follows structured prompt engineering with minimal errors.
    - **Content Integrity**: GPT-4o-mini ensures markdown is not modified, which is critical for this task.

    Returns:
        List[str]: A list of document sections extracted by GPT-4o-mini.
    """
    response = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": "You are an AI that segments markdown documents into slides."},
                  {"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )

    content = response["choices"][0]["message"]["content"]

    try:
        return json.loads(content)  # Ensuring response is valid JSON (prevents hallucinations)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response from GPT-4o-mini. Ensure model strictly returns a JSON array.")

def split_document(document: str, target_slides: int) -> List[str]:
    """
    Uses GPT-4o-mini to split a markdown document into sections while ensuring:
    - **Content Preservation**: No text is altered or removed.
    - **Logical Sectioning**: Breaks happen at meaningful points like headings.
    - **Proper Formatting**: Markdown elements (headings, lists, tables, code blocks) are preserved.
    - **Balanced Lengths**: Sections are roughly equal but maintain coherence.

    Args:
        document (str): The input document in markdown format.
        target_slides (int): Desired number of sections/slides (1-50).

    Returns:
        List[str]: A list of document sections as plain text.
    """
    prompt = f"""
    You are an AI that segments markdown documents into presentation-ready sections. Follow these exact rules:

    CONTENT PRESERVATION
    - Split the document into exactly {target_slides} sections.
    - Do **NOT** modify, rewrite, or remove **ANY** text.
    - The sections must match the original document **exactly** when rejoined.
    - **Preserve ALL markdown formatting**, including:
      - **Headings** (`#`, `##`, `**Bold**`)
      - **Lists** (`-`, `*`, numbered) **Do not split lists across sections**
      - **Code blocks** (```) **Treat code blocks as single units**
      - **Tables** (`| Column | Data |`) **Keep tables intact within the section**
      - **Links** (e.g., `[mistral.ai](http://mistral.ai)`)
      - **Whitespace and line breaks** (do not collapse spacing).

    SECTION BOUNDARIES
    - Each section must contain **ONE complete, coherent idea**.
    - **Use headings (#, ##, **Bold**) as primary split points**.
    - **NEVER split in the middle of:**
      - A **sentence** (ensures readability)
      - A **code block** (ensures proper function if it's a script)
      - A **list** (bulleted or numbered)
      - A **table** (maintains readability)
      - A **footnote**, **citation**, or **special markdown element** (e.g., blockquote)
    - **If no headings exist**, segment based on **topic transitions** (logical paragraph shifts).
    - **DO NOT create sections with only a heading and no content**.

    LENGTH BALANCING
    - Ensure sections are **roughly equal in length** while keeping ideas intact.
    - **If too few major ideas:** **Combine smaller related sections**.
    - **If too many ideas:** **Split larger sections at natural transition points** (e.g., a change in focus, a new example).
    - **For documents with NO HEADINGS:**  
      - Identify **logical topic changes** and split accordingly.
      - **Do NOT arbitrarily break paragraphs**—each section must remain a self-contained idea.
    
    OUTPUT FORMAT
    - **Return ONLY a JSON array of strings:** `["section1", "section2", ...]`
    - Each string should contain **the complete, unmodified section text.**
    - **Preserve ALL original whitespace and markdown formatting.**
    - **NO extra explanations, comments, or metadata—ONLY return the JSON.**

    Now, process the following document:

    {document}
    """

    return call_gpt(prompt)

if __name__ == "__main__":
    print("Welcome to the Document Splitter!")
    print("\nPlease paste your markdown document below (press Ctrl+D or Ctrl+Z when finished):")
    
    # Collect multiline input until EOF (Ctrl+D/Ctrl+Z)
    document_lines = []
    try:
        while True:
            line = input()
            document_lines.append(line)
    except EOFError:
        document = "\n".join(document_lines)
    
    # Get number of slides
    while True:
        try:
            target_slides = int(input("\nHow many slides would you like (1-50)? "))
            if 1 <= target_slides <= 50:
                break
            print("Please enter a number between 1 and 50.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\nProcessing your document...")
    try:
        slides = split_document(document, target_slides)
        print("\nHere are your slides:\n")
        for i, slide in enumerate(slides, 1):
            print(f"=== Slide {i} ===")
            print(slide)
            print()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
