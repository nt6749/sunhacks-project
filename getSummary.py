import base64
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
def justify_tokenizer(fileName):
    with open(fileName, "r", encoding="utf-8") as f:
        data = json.load(f)
    justification = [
        criteria["justification"]
        for criteria in data["criteria"].values()
        if "justification" in criteria
    ]
    return justification


def summerizer(lax_text, strict_text):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )


    summary_prompt = f"Summarize the good and bad of this product from the 2 text in term of eco-friendliness. Must have atleast 1 good and 1 bad comments. Try to keep it short (length < 100 words if possible < 50). split all the good and bad points into bulletpoints first text : {lax_text} second text: {strict_text}"

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=summary_prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.0,
        top_p=1.0,
        thinking_config=types.ThinkingConfig(thinking_budget=256), 
    )
    output_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text: 
            output_text += chunk.text
    return output_text

def getSummerization():
    lax_justification = justify_tokenizer("lax.json")
    strict_justification = justify_tokenizer("strict.json")
    lax_text = " ".join(lax_justification)
    strict_text = " ".join(strict_justification)
    summary = summerizer(lax_text, strict_text)
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    return summary

if __name__ == "main":
    getSummerization()