import openai
try:
    from ..config import Config
except ImportError:
    from config import Config
import logging

class AISummarizer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def summarize(self, content: str) -> str:
        """Create AI summary of content"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You summarise the user-provided text. Output the summary only, no preamble or follow-up questions. ≤200 words, shorter if clear. Informal, friendly, polite. Subtle Manchester UK vibe in phrasing. Professional, unbiased, UK spelling."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=250
            )
            
            summary = response.choices[0].message.content
            logging.info("AI summary generated")
            return summary
            
        except Exception as e:
            logging.error(f"AI summarization error: {e}")
            return content[:200] + "..." if len(content) > 200 else content