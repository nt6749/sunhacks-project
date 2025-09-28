import base64
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def generate_lax_respond(Product):

    student_prompt = f"""You are a sustainability student tasked with ranking the eco-friendliness of a product.
Your goal is to provide an encouraging first-pass score that gives the product the benefit of the doubt.
When researching online, assume good intent if there is any indication of sustainability efforts.
Do not give less than 0.2 for any criterion unless you find clear, negative evidence.
If information is vague or incomplete, lean toward assigning a moderate or slightly above-average score instead of being too harsh.
Marketing claims or company promises can still earn partial credit, even if not fully proven.
Strong, clear evidence should earn high scores, and you may award a 1.0 if the evidence strongly supports it.
If you need to make assumptions (e.g., based on common practices in the industry), clearly state them and still give some credit.
Your job is to be optimistic but fair — avoid penalizing too heavily for missing details.
The product to evaluate is: """ + Product + """
                                     
Scoring criteria (normalize each to 0–1, then apply weights):
1. Reusability (20) – How long the product lasts, how reusable it is, number of uses per lifespan.
2. Company Reputation (25) – Public perception of the company regarding sustainability.
3. Certifications (20) – Eco labels or certifications (FSC, Fair Trade, Energy Star, CarbonNeutral, USDA Organic, etc).
4. Carbon Emissions (15) – Estimated CO₂e impact of manufacturing and shipping.
5. Materials (20) – How recyclable, biodegradable, or renewable the materials are.



Instructions: 
1. Provide a short justification in 2 sentences, less than 30 words for each score, noting whether it is based on hard evidence or cautious inference.
2. Apply the weighted formula to compute an EcoScore (0–100).
3. Give all the urls you used as evidence at the end.
4. Use Google Search to find relevant information about the product and company before scoring.
5. Don't return any extra commentary or text outside the JSON. this including sources used.
5. Return JSON only in this exact structure:

{
  "product": "<product name>",
  "criteria": {
    "reusability": {"score": 0.x, "justification": "..."},
    "company_reputation": {"score": 0.x, "justification": "..."},
    "certifications": {"score": 0.x, "justification": "..."},
    "carbon_emissions": {"score": 0.x, "justification": "..."},
    "materials": {"score": 0.x, "justification": "..."}
  },
  "eco_score": 0.xx
}
"""

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )


    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=student_prompt),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.0,
        top_p=1.0,
        thinking_config=types.ThinkingConfig(thinking_budget=256), 
        tools=tools,
        
    )
    output_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
        
    ):
        if chunk.text: 
            output_text += chunk.text
        
    output_text = clean_json_output(output_text)
    
    with open("lax.json", "w", encoding="utf-8") as f:
        f.write(output_text)
    return output_text




def generate_strict_respond(reusability_score, company_score, certifications_score, carbon_score, materials_score):

    professor_prompt = f"""
        You are a strict professor reviewing eco-friendliness scores.

        Here are the student's baseline scores:
        - Reusability: {reusability_score}
        - Company Reputation: {company_score}
        - Certifications: {certifications_score}
        - Carbon Emissions: {carbon_score}
        - Materials: {materials_score}

        Rules:
        - These numbers are your starting point.
        - Provide a short justification in 2 sentences, less than 30 words commenting on the product's sustainability for each score, noting whether it is based on hard evidence or cautious inference.
        - You may subtract 0.1 to 0.3 if evidence is weak.
        - If evidence is strong, keep the same.
        - You can never increase above the baseline.
        - Use Google Search to verify whether each justification has real evidence.
        

        Return JSON only do not add any commentary or extra text, only the JSON in this exact structure:
        {{
        "criteria": {{
            "reusability": {{"strict_score": 0.x, "justification": "..."}},
            "company_reputation": {{"strict_score": 0.x, "justification": "..."}},
            "certifications": {{"strict_score": 0.x, "justification": "..."}},
            "carbon_emissions": {{"strict_score": 0.x, "justification": "..."}},
            "materials": {{"strict_score": 0.x, "justification": "..."}}
        }},
        "eco_score_strict": 0.xx
        }}
        """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=professor_prompt),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.0,
        top_p=1.0,
        thinking_config=types.ThinkingConfig(thinking_budget=256), 
        tools=tools,
        
    )
    output_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
       
    ):
        if chunk.text: 
            output_text += chunk.text
    
    output_text = clean_json_output(output_text)

    with open("strict.json", "w", encoding="utf-8") as f:
        f.write(output_text)
    return output_text


def clean_json_output(raw_text) -> str:
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```", 1)[1]  # remove first ```
    if raw_text.startswith("json"):
        raw_text = raw_text[len("json"):].strip()
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("```", 1)[0]
    return raw_text.strip()



def main(product):
    lax_respond = generate_lax_respond(product)
    lax_data = json.loads(lax_respond)

    reusability_score = lax_data["criteria"]["reusability"]["score"]
    company_score = lax_data["criteria"]["company_reputation"]["score"]
    certifications_score = lax_data["criteria"]["certifications"]["score"]
    carbon_score = lax_data["criteria"]["carbon_emissions"]["score"]
    materials_score = lax_data["criteria"]["materials"]["score"]

    eco_score_lax = (reusability_score * 20) + (company_score * 25) + (certifications_score * 20) + (carbon_score * 15) + (materials_score * 20)
    print(f"Eco Score (Lax): {eco_score_lax}")

    strict_respond = generate_strict_respond(reusability_score=reusability_score, company_score=company_score, certifications_score=certifications_score, carbon_score=carbon_score, materials_score=materials_score)
    strict_data = json.loads(strict_respond)

    strict_reusability_score = strict_data["criteria"]["reusability"]["strict_score"]
    strict_company_score = strict_data["criteria"]["company_reputation"]["strict_score"]
    strict_certifications_score = strict_data["criteria"]["certifications"]["strict_score"] 
    strict_carbon_score = strict_data["criteria"]["carbon_emissions"]["strict_score"]
    strict_materials_score = strict_data["criteria"]["materials"]["strict_score"]

    eco_score_strict = (strict_reusability_score * 20) + (strict_company_score * 25) + (strict_certifications_score * 20) + (strict_carbon_score * 15) + (strict_materials_score * 20)
    print(f"Eco Score (Strict): {eco_score_strict}")

    print("total score: " + str((eco_score_lax + eco_score_strict)/2))
    
    

if __name__ == "__main__":
    product = "Boka Classic Manual Toothbrush with Extra Soft Activated-Charcoal, Tapered Bristles, Bioplastic Handle That Includes Travel Cap, Dentist-Approved, Great for Adults and Kids, Multi Color"
    main(product)

