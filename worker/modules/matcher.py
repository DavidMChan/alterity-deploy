import sys
import os
from typing import List, Dict, Any, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Backstory

class Matcher:
    def __init__(self):
        pass

    def calculate_weight(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """
        Calculates the weight (probability product) of matching a target to a candidate.
        Equation 1 from Alterity paper: Product P(d_jl = t_il)
        """
        weight = 1.0
        candidate_demographics = candidate.get("demographics", {})

        # If candidate has no demographics, improved fallback or just 0
        if not candidate_demographics:
            return 0.001

        for trait_key, target_value in target.items():
            # Skip metadata keys
            if trait_key in ["id", "custom_tags"]:
                continue

            cand_trait_data = candidate_demographics.get(trait_key)
            prob = 0.0

            # Handle Distribution (Dictionary)
            if isinstance(cand_trait_data, dict):
                prob = cand_trait_data.get(str(target_value), 0.0)
            # Handle Deterministic Value
            else:
                # Loose string matching for robust comparison
                if str(cand_trait_data).lower() == str(target_value).lower():
                    prob = 1.0
                else:
                    prob = 0.01 # Small epsilon for soft matching

            weight *= prob

        return weight

    def perform_matching(self, targets: List[Dict[str, Any]], candidates: List[Dict[str, Any]]) -> List[Tuple[Dict, Dict]]:
        """
        Uses Hungarian Algorithm (Maximum Weight Matching) to find optimal assignment.
        Since linear_sum_assignment finds minimum cost, we use Cost = -Weight.
        """
        if not targets or not candidates:
            return []

        # Cost matrix: Rows = Targets, Cols = Candidates
        # We need a square matrix for standard assignment or rectangular is fine for scipy?
        # Scipy handles rectangular: "The method used is the Hungarian algorithm, also known as the Munkres algorithm."
        # It assigns min(n, m) elements.

        n_targets = len(targets)
        n_candidates = len(candidates)

        # Initialize with high cost (effectively 0 weight)
        cost_matrix = np.zeros((n_targets, n_candidates))

        for i, target in enumerate(targets):
            for j, candidate in enumerate(candidates):
                w = self.calculate_weight(target, candidate)
                cost_matrix[i, j] = -w  # Negate for maximization

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        matches = []
        for i, j in zip(row_ind, col_ind):
            # Only include if the match has a reasonable weight (or keeps it anyway?)
            # The algorithm forces assignments.
            matches.append((targets[i], candidates[j]))

        return matches

    def match_against_db(self, targets: List[Dict[str, Any]]) -> List[Tuple[Dict, Dict]]:
        """
        Fetches all backstories from DB and matches against targets.
        """
        db = SessionLocal()
        try:
            # Fetch all backstories
            # In production this would be filtered or use vector search first
            backstories_orm = db.query(Backstory).all()

            if not backstories_orm:
                print("[Matcher] No backstories found in DB.")
                return []

            # Convert to dict format expected by logic
            candidates = []
            for b in backstories_orm:
                candidates.append({
                    "id": b.id,
                    "content": b.content,
                    "demographics": b.demographics,
                    "custom_tags": b.custom_tags
                })

            return self.perform_matching(targets, candidates)

        finally:
            db.close()

# Singleton
matcher = Matcher()
