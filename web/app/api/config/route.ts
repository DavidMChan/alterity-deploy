
import { NextResponse } from "next/server"

export async function GET() {
    // In a real app, we might fetch from Supabase here to get the 'updated' values.
    // For now, we can hardcode the SAME defaults as the worker to expose them to the frontend,
    // OR ideally fetching from the 'configurations' table via Supabase client.

    // Let's return a hardcoded structure that matches ConfigManager's defaults for now to unblock UI,
    // since the worker is the source of truth for execution.
    // Ideally we'd sync this.

    return NextResponse.json({
        available_models: [
            { id: "gpt-4-turbo", name: "GPT-4 Turbo" },
            { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo" },
            { id: "llama-3-70b", name: "Llama 3 70B (Groq/OpenRouter)" },
            { id: "meta-llama/Meta-Llama-3-8B-Instruct", name: "Local vLLM (Llama 3 8B)" }
        ],
        feature_flags: {
            "enable_advanced_metrics": false,
            "enable_csv_export": true
        }
    })
}
