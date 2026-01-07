import { NextResponse } from "next/server"
import Redis from "ioredis"
import { createClient } from "@supabase/supabase-js"

// Redis connection - using Generic Redis string or Upstash
const redis = new Redis(process.env.REDIS_URL || "redis://localhost:6379")

// Admin Supabase Client for backend ops
const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY! // fallback for now
)

export async function POST(req: Request) {
    try {
        const { surveyId, configId, methodology, userId, modelName } = await req.json()

        // 1. Create Survey Run Entry
        const { data: run, error } = await supabase
            .from("survey_runs")
            .insert({
                survey_id: surveyId,
                config_id: configId,
                methodology,
                run_config: { model_name: modelName || "gpt-4-turbo" },
                status: "QUEUED"
            })
            .select()
            .single()

        if (error) {
            console.error("DB Error", error)
            return NextResponse.json({ error: error.message }, { status: 500 })
        }

        // 2. Dispatch to Redis
        await redis.lpush("alterity_jobs", JSON.stringify({
            job_type: "RUN_SURVEY",
            run_id: run.id,
            methodology,
            run_config: { model_name: modelName || "gpt-4-turbo" }
        }))

        return NextResponse.json({ runId: run.id })

    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 })
    }
}
