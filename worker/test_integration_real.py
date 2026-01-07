import sys
import os
import time
from typing import Dict, Any

from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.append(os.getcwd())

from database import SessionLocal, Survey, SurveyRun, Probe, Result, get_db
from modules.runner import execute_run
from modules.backstory_generator import generator

@patch('llm.openai_client.chat.completions.create')
@patch('modules.runner.SessionLocal')
def test_integration(mock_session_cls, mock_create):
    print("=== Starting Integration Test (Fully Mocked) ===")

    # Setup LLM Mock
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a mocked response."
    mock_response.usage.prompt_tokens = 50
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 70
    mock_create.return_value = mock_response

    # Setup DB Mock
    mock_db = MagicMock()
    mock_session_cls.return_value = mock_db

    # Mock entities
    mock_run = MagicMock()
    mock_run.id = 1
    mock_run.status = "QUEUED"
    mock_run.methodology = "DEMOGRAPHIC_FORCING"
    mock_run.survey_id = 99

    mock_probe = MagicMock()
    mock_probe.id = 101
    mock_probe.content = "Test question"
    mock_probe.survey_id = 99

    # Configure query results
    # db.query(SurveyRun).filter(...).first() -> mock_run
    mock_db.query.return_value.filter.return_value.first.return_value = mock_run
    # db.query(Probe).filter(...).all() -> [mock_probe]
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_probe]

    try:
        # Execute Run directly
        print(f"\n[Step 4] Executing Run ID: {mock_run.id}...")
        payload = {"run_id": mock_run.id}
        execute_run(payload)

        # 5. Verify Results being added to DB
        print("\n[Step 5] Verifying DB interactions...")
        # Check that db.add was called with a Result object
        added_objs = [call[0][0] for call in mock_db.add.call_args_list]
        result_objs = [obj for obj in added_objs if isinstance(obj, Result)]

        print(f"Found {len(result_objs)} generated results passed to db.add().")

        if len(result_objs) > 0:
            res = result_objs[0]
            print(f"Sample Response: {res.response}")
            # Calculate expected cost: 0.0005*(50/1000) + 0.0015*(20/1000) = 0.000025 + 0.000030 = 0.000055
            print(f"Usage Cost: {res.usage_cost}")
            if res.usage_cost > 0:
                print("SUCCESS: Cost calculation working.")
            else:
                print("WARNING: Cost is 0.")
        else:
            print("FAILURE: No results generated.")

    except Exception as e:
        print(f"Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integration()
