import sys
import os
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import chat_completion
from database import SessionLocal, Backstory

class BackstoryGenerator:
    def __init__(self, model_name: str = "gpt-4-turbo"):
        self.model_name = model_name
        # Questions from Alterity Paper Appendix A
        self.questions = [
            "To start, I would like to begin with a big question: tell me the story of your life. Start from the beginning–from your childhood, to education, to family and relationships, and to any major life events you may have had.",
            "Some people tell us that they’ve reached a crossroads at some points in their life where multiple paths were available, and their choice then made a significant difference in defining who they are. What about you? Was there a moment like that for you, and if so, could you tell me the whole story about that from start to finish?",
            "Tell me about anyone else in your life we haven’t discussed (like friends or romantic partners). Are there people outside of your family who are important to you?",
            "Now let’s talk about your current neighborhood. Tell me all about the neighborhood and area in which you are living now.",
            "Tell me about any recent changes to your daily routine.",
            "How would you describe your political views?",
            "How have you been thinking about race in the U.S. recently?",
            "For you, what makes it easy or hard to stay healthy?",
            "Some people are excited about medical vaccination, and others, not so much. How about you?",
            "Some people say they struggle with depression, anxiety, or something else like that. How about for you?"
        ]

    def _format_context(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": "You are participating in an interview. Answer the interviewer's questions naturally and consistently with your previous answers."}]
        for turn in history:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        return messages

    def critique_response(self, context_str: str, response: str) -> bool:
        """
        Uses a critic model to check for consistency and relevance.
        """
        system_prompt = (
            "You are a strict critic. Check the following interview response for:"
            "1. Internal consistency with previous context.\n"
            "2. Natural flow (no code, no repetitive phrases, no metadata).\n"
            "3. Relevance to the question.\n"
            "Respond with 'YES' if good, 'NO' if bad."
        )
        content = f"Context:\n{context_str}\n\nResponse:\n{response}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]

        try:
            # Using a faster/cheaper model for critique
            resp = chat_completion(messages, model="gpt-3.5-turbo")
            return "YES" in resp["content"].strip().upper()
        except Exception as e:
            print(f"[Critic Error] {e}")
            return True # Fail open if critic breaks? Or fail closed? Falling open for prototype.

    def generate_interview(self, seed_bio: str) -> str:
        history = []
        # Pre-seed the history optionally, or just let the first question drive it
        # based on a system prompt that includes the seed.

        full_transcript = []

        print(f"[Generator] Starting interview for seed: {seed_bio[:30]}...")

        for i, question in enumerate(self.questions):
            messages = self._format_context(history)
            # Inject the seed instructions only in the very first system message or first user message
            if i == 0:
                messages[0]["content"] += f"\n\nPersona Seed: {seed_bio}"

            messages.append({"role": "user", "content": question})

            valid = False
            attempts = 0
            best_response = ""

            while not valid and attempts < 3:
                resp_data = chat_completion(messages, model=self.model_name)
                candidate = resp_data["content"]

                # Context string for critic
                context_str = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
                if self.critique_response(context_str, candidate):
                    best_response = candidate
                    valid = True
                else:
                    print(f"[Critic] Rejected response for Q{i+1}. Retrying...")
                    attempts += 1

            if not valid:
                print(f"[Generator] Valid response failed for Q{i+1} after 3 attempts. Accepting last candidate.")
                best_response = candidate

            history.append({"question": question, "answer": best_response})
            full_transcript.append(f"Interviewer: {question}\nParticipant: {best_response}")
            print(f"[Generator] Completed Q{i+1}/10")

        return "\n\n".join(full_transcript)

    def run_pipeline(self, num_backstories: int = 1, model_name: str = None) -> List[Dict[str, Any]]:
        # Override model if provided
        if model_name:
            self.model_name = model_name

        db = SessionLocal()
        results = []

        try:
            for _ in range(num_backstories):
                # 1. Selection / Seeding
                import random
                SEED_POOL = [
                    "A 30-year-old nurse from Ohio who votes Independent.",
                    "A 55-year-old truck driver from Alabama, strictly Republican.",
                    "A 22-year-old college student in California studying Art, very liberal.",
                    "A 40-year-old software engineer in Seattle, libertarian leaning.",
                    "A 65-year-old retiree in Florida, concerned about social security.",
                    "A 28-year-old teacher in Chicago, active in unions.",
                    "A 45-year-old small business owner in Texas.",
                    "A 35-year-old stay-at-home parent in Utah.",
                    "A 50-year-old factory worker in Michigan.",
                    "A 25-year-old barista in Portland, Oregon."
                ]
                seed = random.choice(SEED_POOL)

                # 2. Multi-turn Generation
                transcript = self.generate_interview(seed)

                # 3. Save
                # In a real app we'd parse demographics using `dynamic_labeler`.
                # For now using the seed as placeholder or extracted elsewhere.
                demographics = {}

                backstory = Backstory(
                    content=transcript,
                    model_signature=self.model_name,
                    demographics=demographics,
                    custom_tags={"seed": seed}
                )
                db.add(backstory)
                results.append(backstory)
                db.commit() # Commit each one

            print(f"[Generator] Saved {len(results)} backstories.")

        except Exception as e:
            print(f"[Generator Error] {e}")
            db.rollback()
        finally:
            db.close()

        return [{"id": b.id, "content": b.content} for b in results]

# Singleton instance
generator = BackstoryGenerator()
