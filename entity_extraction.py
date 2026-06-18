import os
import json
from dotenv import load_dotenv
import anthropic
load_dotenv()
client=anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
EXTRACTION_PROMPT="""You are an information extraction system.
Read the text below and extract factual relationships as triples.
 
Return ONLY a JSON array, no other text. Each item must look like:
{{"subject": "Entity A", "relation": "RELATION_TYPE", "object": "Entity B"}}
 
Rules:
- Use short, UPPER_SNAKE_CASE relation types (e.g. FOUNDED_BY, LOCATED_IN, ACQUIRED).
- Keep entity names short and consistent (use the same string for the same entity every time it appears).
- Extract only relationships that are clearly stated, not inferred or guessed.
- Extract at most 15 triples per text chunk.
 
Text:
{text}
"""
def extract_triples(text:str)->list[dict]:
    response=client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role":"user","content":EXTRACTION_PROMPT.format(text=text)}],
    )
    raw=response.content[0].text.strip()
    raw=raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        triples=json.loads(raw)
    except json.JSONDecodeError:
        print("Failed to parse model",raw)
        return []
    return triples
def chunk_text(text:str,max_chars:int=2000)->list[str]:
    return [text[i:i+max_chars] for i in range(0,text,max_chars)]
def extract_from_document(text:str)->list[dict]:
    all_triples=[]
    for chunk in chunk_text(text):
        all_triples.extend(extract_triples(chunk))
    return all_triples
if __name__=="__main__":
    sample="""Tata Consultancy Services was founded by the Tata Group in 1968.
    TCS is headquartered in Mumbai. N. Chandrasekaran is the chairman of Tata Sons,
    which is the parent company of TCS."""
    triples=extract_from_document(sample)
    print(json.dumps(triples,indent=2))