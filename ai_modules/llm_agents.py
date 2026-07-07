from openai import OpenAI

def generate_blending_advice(api_key, wine_profiles, target_style):
    """
    Uses OpenAI API to generate an agentic master blending recommendation.
    """
    if not api_key:
        return {"error": "API Key is required."}
    
    try:
        # Determine base URL if it's DeepSeek
        if api_key.startswith("sk-") and len(api_key) == 35: # very loose heuristic for deepseek
             client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
             model = "deepseek-chat"
        else:
             client = OpenAI(api_key=api_key)
             model = "gpt-4o-mini" # or gpt-3.5-turbo

        prompt = f"""You are an elite Master Enologist and Sommelier.
I have several lots of wine with the following profiles:
{wine_profiles}

My target style is: {target_style}

Act as an AI Master Blender. Analyze the strengths and weaknesses of each lot and propose a percentage-based blending ratio to achieve the target style. Explain your reasoning scientifically (referencing pH, TA, tannins, and aroma compounds). Keep it concise, professional, and directly actionable.
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Master Enologist AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
