
import os
import json
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from database import SessionLocal, Configuration, FeatureFlag

class ConfigManager:
    _instance = None

    # Defaults
    DEFAULT_PRICING = {
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "default": {"input": 0.50, "output": 1.50}
    }

    DEFAULT_SEED_POOL = [
        "A 30-year-old nurse from Ohio who votes Independent.",
        "A 55-year-old truck driver from Alabama, strictly Republican.",
        "A 22-year-old college student in California studying Art, very liberal.",
        "A 40-year-old software engineer in Seattle, libertarian leaning.",
        "A 65-year-old retiree in Florida, concerned about social security.",
    ]

    DEFAULT_QUESTIONS = [
        "To start, I would like to begin with a big question: tell me the story of your life.",
        "Tell me about any recent changes to your daily routine.",
        "How would you describe your political views?"
    ]

    DEFAULT_LOCAL_MODELS = [
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "meta-llama/Meta-Llama-3-70B-Instruct"
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def _get_config(self, key: str, default: Any) -> Any:
        db: Session = SessionLocal()
        try:
            config = db.query(Configuration).filter(Configuration.key == key).first()
            if config:
                return config.value
            return default
        except Exception as e:
            print(f"[ConfigManager Error] Failed to fetch {key}: {e}")
            return default
        finally:
            db.close()

    def get_pricing(self) -> Dict[str, Dict[str, float]]:
        return self._get_config("PRICING_MODEL", self.DEFAULT_PRICING)

    def get_seed_pool(self) -> List[str]:
        return self._get_config("SEED_POOL", self.DEFAULT_SEED_POOL)

    def get_interview_questions(self) -> List[str]:
        return self._get_config("INTERVIEW_QUESTIONS", self.DEFAULT_QUESTIONS)

    def get_local_models(self) -> List[str]:
        return self._get_config("LOCAL_MODELS", self.DEFAULT_LOCAL_MODELS)

    def is_flag_enabled(self, flag_name: str, default: bool = False) -> bool:
        db: Session = SessionLocal()
        try:
            flag = db.query(FeatureFlag).filter(FeatureFlag.name == flag_name).first()
            if flag:
                return flag.is_enabled
            return default
        except Exception as e:
            print(f"[ConfigManager Error] Failed to fetch flag {flag_name}: {e}")
            return default
        finally:
            db.close()

config_manager = ConfigManager()
