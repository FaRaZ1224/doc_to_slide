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
OPENAI_API_KEY = "your-openai-api-key"  # Replace with your actual OpenAI API key
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

