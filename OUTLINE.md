Here is a scalable architectural specification for the **Alterity Webapp**. This architecture separates the lightweight application logic (Next.js/Supabase) from the heavy compute/inference logic (Python/GPU Workers), ensuring the system is responsive and scalable.

### 1. High-Level Architecture

The system follows an asynchronous **Job Queue** pattern.

* **Frontend (Vercel):** Next.js App for UI, Auth, and Survey Configuration.
* **Backend API (Vercel Serverless):** Handles CRUD, billing logic, and dispatches jobs.
* **Database (Supabase):** PostgreSQL for relational data, Auth, and JSONB storage for dynamic demographics.
* **Message Broker (Redis):** Manages the communication between the API and GPU workers.
* **Inference Engine (GPU Workers):** Dockerized Python containers running on GPU cloud (e.g., RunPod, Lambda Labs, or AWS GPU instances). This layer executes the specific methodologies from the paper (Backstory generation, Critic loops, Hungarian matching, and Probe inference).

---

### 2. Database Schema (Supabase PostgreSQL)

The schema is designed to handle the complex many-to-many relationships between surveys, backstories, and dynamic demographic tags.

#### **Core Entities**

* **`users`**: Extends Supabase Auth (Profile data, Credit balance, Plan tier).
* **`surveys`**: Metadata (Name, Description, Status, Created_By).
* **`probes`**: The specific questions in a survey.
* `content`: Text (e.g., "Would you support freezing social media accounts...?").
* `type`: Multiple Choice / Open Ended.


* **`demographic_configs`**: Stores the user's target demographic settings for a specific run.
* `constraints`: JSONB (e.g., `{"age": "18-24", "party": "Republican", "custom_trait": "owns_tesla"}`).



#### **The Persona Engine**

* **`backstories`**: The central asset.
* `content`: TEXT (The full generated interview transcript).
* `model_signature`: STRING (Which model generated it, e.g., "Llama-3-70B").
* `demographics`: JSONB (Pre-labeled tags: `{ "age": "...", "gender": "...", "politics": "..." }`).
* `custom_tags`: JSONB (Dynamic tags learned over time: `{ "owns_tesla": true, "likes_scifi": false }`).
* `embedding`: VECTOR (Optional, for semantic search matching).



#### **Execution & Results**

* **`survey_runs`**: An instance of a survey being executed.
* `methodology`: ENUM ('ALTERITY', 'DEMOGRAPHIC_FORCING', 'SIMPLE_PERSONA').
* `status`: ENUM ('QUEUED', 'MATCHING', 'INFERENCE', 'COMPLETED').


* **`results`**:
* `run_id`: FK.
* `probe_id`: FK.
* `backstory_id`: FK (Links the specific persona used).
* `response`: JSONB (The model's output).
* `usage_cost`: FLOAT (Compute cost for this specific row).



---

### 3. The "Alterity" Engine (Python GPU Worker)

This is the core differentiator. It should be a Python application (FastAPI + Celery) running in a Docker container with access to GPUs (or high-throughput API keys).

#### **Module A: The Backstory Generator (Background Job)**

* **Trigger:** Runs periodically or when `backstory_pool` count is low.
* **Process (Paper Methodology):**
1. **Interview Loop:** Iterates through the "American Voices Project" questions.
2. **Critic Loop:** Uses a smaller, fast model (e.g., GPT-4o-mini or Llama-8B) as the "Judge" to check for consistency and hallucination (e.g., ensuring "born in 1990" stays consistent).
3. **Storage:** Saves the validated transcript to `backstories`.



#### **Module B: The Dynamic Labeler (On-Demand Job)**

* **Trigger:** When a user requests a demographic trait not present in the standard schema (e.g., "People who like Sci-Fi").
* **Process:**
1. Selects a subset of `backstories`.
2. **Zero-Shot Classification:** Feeds the backstory to an LLM with the prompt: *"Does the author of this text like Sci-Fi? Answer Yes/No/Unknown."*
3. **Update:** Writes the result to `backstories.custom_tags`.



#### **Module C: The Matcher & Runner (Survey Execution Job)**

* **Trigger:** User clicks "Run Survey".
* **Step 1: Population Matching (The Hungarian Algorithm):**
* Fetch available backstories.
* Calculate the "Edge Weight" between the User's Target Demographics and the Backstory's attributes (as defined in Appendix F of the paper).
* Perform Bipartite Matching to select the optimal set of backstories.
* *Fallback:* If insufficient matches exist, trigger **Module A** (Generation) with specific seeding prompts to fill the gap.


* **Step 2: Probe Inference:**
* **Method 1 (Alterity):** Context Window = `[Backstory Transcript]` + `[Probe Question]`.
* **Method 2 (Demographic Forcing):** Context Window = `[System Prompt: You are a Republican...]` + `[Probe Question]`.
* **Engine:** Uses `vLLM` for high-throughput batch inference if self-hosting, or async API calls.


* **Step 3: Result Aggregation:** Batch insert results into Supabase.

---

### 4. API & Frontend Workflow

#### **1. Survey Creation**

* **User Action:** User creates a survey and adds probes.
* **Tech:** Standard React Forms -> Supabase INSERT.

#### **2. Demographic Configuration (The "Target")**

* **User Action:** User selects "Republicans, Age 18-35" AND "Must like Sci-Fi".
* **Tech:**
* Frontend checks `demographic_configs`.
* If "Must like Sci-Fi" is a new tag, the API flags this run as requiring **Dynamic Labeling**.



#### **3. Execution**

* **User Action:** Clicks "Launch".
* **API:**
* Checks User Credit Balance.
* Creates a `survey_run` entry (Status: QUEUED).
* Pushes a payload to Redis: `{'job_type': 'RUN_SURVEY', 'run_id': 123, 'config': ...}`.



#### **4. Visualization**

* **User Action:** Views results.
* **Tech:**
* **Distribution Plots:** Use libraries like `Recharts` or `Visx` to plot the "Wasserstein Distance" or simple bar charts comparing the Virtual Persona responses vs. expected baselines.
* **Drill Down:** User can click a data point to see the *specific backstory* that generated that response (The "Why").



---

### 5. Monetization & Tracking Infrastructure

To turn this into a product, tracking must be granular.

* **Token Ledger:**
* Every call in the Python Worker calculates input/output tokens.
* After every batch, the Worker updates the `survey_runs` table with `tokens_used`.
* A Supabase Database Trigger deducts credits from `users.balance`.


* **Tiered Access:**
* **Free:** Use "Demographic Forcing" (Cheap, shallow).
* **Pro:** Use "Alterity/Backstories" (Expensive, deep binding).
* **Enterprise:** Custom Dynamic Demographics (Requires running the Labeling Module on thousands of backstories).



### 6. Recommended Stack Summary

| Component | Technology | Reasoning |
| --- | --- | --- |
| **Frontend** | **Next.js (Vercel)** | Fast iteration, built-in API routes. |
| **Auth/DB** | **Supabase** | Instant Postgres, Row Level Security, Auth UI. |
| **Job Queue** | **Upstash Redis** (or generic Redis) | Serverless Redis, pairs well with Vercel. |
| **Worker Logic** | **Python (FastAPI + Celery)** | Native support for PyTorch/HuggingFace/vLLM. |
| **Inference** | **vLLM (Dockerized)** | Highest throughput serving engine for LLMs. |
| **Compute** | **RunPod / Lambda Labs** | Cost-effective GPU rental for batch jobs. |

### 7. Implementation Roadmap (Next Steps)

1. **Phase 1 (The Skeleton):** Set up Supabase schema and Next.js frontend. Create the "Backstory" table and seed it with 50 manually generated transcripts.
2. **Phase 2 (The Simple Runner):** Build the Python worker to read from Redis, perform simple Demographic Forcing (Prompting), and write results.
3. **Phase 3 (The Deep Binding):** Implement the "Backstory Generator" loop in the Python worker using vLLM. Populate the DB with ~1k backstories.
4. **Phase 4 (The Matcher):** Implement the Hungarian Matching algorithm in the worker to select backstories based on user config.
5. **Phase 5 (Dynamic Tags):** Add the "Labeler" module to handle custom user demographics.
