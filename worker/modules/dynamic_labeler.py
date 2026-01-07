import sys
import os
from typing import List, Dict, Any, Union

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import chat_completion
from database import SessionLocal, Backstory

class DynamicLabeler:
    def __init__(self):
        pass

    def check_trait(self, backstory_content: str, trait: str) -> str:
        """
        Uses an LLM to check if the text implies a specific trait.
        Returns 'Yes', 'No', or 'Unknown'.
        """
        prompt = (
            f"Does the author of this text explicitly or implicitly indicate that they '{trait}'? "
            "Answer with exactly one word: Yes, No, or Unknown.\n\n"
            f"Text: {backstory_content[:2000]}..."
        )

        messages = [
            {"role": "system", "content": "You are a zero-shot classifier."},
            {"role": "user", "content": prompt}
        ]

        print(f"[Labeler] Checking trait '{trait}'...")
        response_data = chat_completion(messages, model="gpt-3.5-turbo")
        content = response_data["content"]

        # Clean response
        cleaned = content.strip().lower()
        if "yes" in cleaned:
            return "Yes"
        elif "no" in cleaned:
            return "No"
        return "Unknown"

    def label_backstories_in_db(self, trait: str, limit: int = 100):
        """
        Scans backstories in DB and updates them with the trait tag.
        """
        db = SessionLocal()
        try:
            # Get backstories that don't have this tag yet
            # JSONB query is a bit complex in pure ORM, so fetching all for now or raw SQL
            # For simplicity: Fetch all, check if tag exists in custom_tags
            backstories = db.query(Backstory).all()

            updates = 0
            for bs in backstories:
                current_tags = bs.custom_tags or {}
                if trait in current_tags:
                    continue

                result = self.check_trait(bs.content, trait)

                if result == "Yes":
                    current_tags[trait] = True
                    updates += 1
                elif result == "No":
                    current_tags[trait] = False
                    updates += 1
                else:
                    # Mark as unknown/checked so we don't re-check?
                    # For now just leaving it absent implies unknown
                    pass

                # SQLAlchemy requires flagging modified for JSONB mutations sometimes
                bs.custom_tags = dict(current_tags)

            db.commit()
            print(f"[Labeler] Updated {updates} backstories with trait '{trait}'.")

        except Exception as e:
            print(f"[Labeler Error] {e}")
            db.rollback()
        finally:
            db.close()

# Singleton
labeler = DynamicLabeler()
