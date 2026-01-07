import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, SurveyRun, Result, Probe, DemographicConfig, Backstory
from llm import chat_completion
from .matcher import matcher
from .matcher import matcher
from .demographic_forcing import run_demographic_forcing
from modules.config_manager import config_manager

def calculate_cost(usage: Dict[str, int], model: str = "gpt-4-turbo") -> float:
    pricing = config_manager.get_pricing()

    # Simple logic to find best match or default
    rates = pricing.get(model, pricing.get("default", {"input": 0.50, "output": 1.50}))

    input_cost = (usage.get("prompt_tokens", 0) / 1000_000) * rates["input"]
    output_cost = (usage.get("completion_tokens", 0) / 1000_000) * rates["output"]
    return input_cost + output_cost

def execute_run(payload: Dict[str, Any]):
    """
    Main entry point for executing a survey run.
    Payload: { 'run_id': 123 }
    """
    run_id = payload.get("run_id")
    print(f"[Runner] Starting execution for Run ID: {run_id}")

    db = SessionLocal()
    try:
        # Fetch Run Data
        run = db.query(SurveyRun).filter(SurveyRun.id == run_id).first()
        if not run:
            print(f"[Runner Error] Run ID {run_id} not found.")
            return

        run.status = "MATCHING"
        db.commit()

        # Fetch Related Data
        probes = db.query(Probe).filter(Probe.survey_id == run.survey_id).all()
        config = db.query(DemographicConfig).filter(DemographicConfig.id == run.config_id).first() if run.config_id else None

        target_demographics = config.constraints if config else {}

        results_count = 0

        # Extract Model Config
        model_name = "gpt-4-turbo" # Default
        if run.run_config and "model_name" in run.run_config:
            model_name = run.run_config["model_name"]

        print(f"[Runner] Starting execution for Run ID: {run_id} with Model: {model_name}")

        if run.methodology == "DEMOGRAPHIC_FORCING":
            run.status = "INFERENCE"
            db.commit()

            # Run Demographic Forcing
            results_data = []
            total_tokens_used = 0
            total_cost = 0.0
            for probe in probes:
                # Generate system prompt based on demographics
                response = run_demographic_forcing(probe.content, target_demographics, model=model_name)

                results_data.append({
                    "probe_id": probe.id,
                    "response": response["content"],
                    "usage": response.get("usage", {})
                })

                # Simple aggregation of cost (approx)
                # In production, track per-model pricing
                total_tokens_used += response.get("usage", {}).get("total_tokens", 0)

                # Calculate cost (using generic GPT-4 rates for now as placeholder or map)
                cost = calculate_cost(response.get("usage", {}), model=model_name)

                total_cost += cost

            # Save results... logic continues below
            for item in results_data:
                result = Result(
                    run_id=run.id,
                    probe_id=item["probe_id"],
                    backstory_id=None,
                    response={"text": item["response"]},
                    usage_cost=total_cost / len(results_data) if results_data else 0 # Distribute total cost evenly for now
                )
                db.add(result)
                results_count += 1

        elif run.methodology == "ALTERITY":
            # 1. Matching
            matches = matcher.match_against_db([target_demographics])
            # Matches returns list of (target, candidate_dict) strings
            # We assume we just want the best N matches for the population size
            # For simplicity, let's take top 5 matches
            top_matches = matches[:5]

            run.status = "INFERENCE"
            db.commit()

            for target, backstory_data in top_matches:
                # Re-fetch full backstory if needed, or use data
                # Run inference
                for probe in probes:
                    # Construct Contextual Prompt
                    system_prompt = (
                        "You are the person described in the following backstory. "
                        "Answer the question as this person would, maintaining their tone, memories, and opinions.\n\n"
                        f"Backstory: {backstory_data['content']}"
                    )
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": probe.content}
                    ]

                    response_data = chat_completion(messages)
                    cost = calculate_cost(response_data.get("usage", {}), model=model_name)

                    result = Result(
                        run_id=run.id,
                        probe_id=probe.id,
                        backstory_id=backstory_data['id'],
                        response={"text": response_data["content"]},
                        usage_cost=cost
                    )
                    db.add(result)
                    results_count += 1

        else:
            print(f"[Error] Unknown methodology: {run.methodology}")
            run.status = "FAILED"
            db.commit()
            return

        run.status = "COMPLETED"
        run.completed_at = datetime.utcnow()
        db.commit()
        print(f"[Runner] Completed Run {run_id} with {results_count} results.")

    except Exception as e:
        print(f"[Runner Error] {e}")
        db.rollback()
        # Re-fetch to update status safely
        try:
           run = db.query(SurveyRun).filter(SurveyRun.id == run_id).first()
           if run:
               run.status = "FAILED"
               db.commit()
        except:
            pass
    finally:
        db.close()
