"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase"
import { Loader2, Play } from "lucide-react"

export default function RunSurveyPage({ params }: { params: { id: string } }) {
    const router = useRouter()
    const supabase = createClient()

    const [loading, setLoading] = useState(false)
    const [survey, setSurvey] = useState<any>(null)

    // Demographics state
    const [demographics, setDemographics] = useState({
        age: "all",
        party: "all",
        custom: ""
    })

    const [methodology, setMethodology] = useState("DEMOGRAPHIC_FORCING") // or ALTERITY
    const [modelName, setModelName] = useState("gpt-4-turbo")
    const [availableModels, setAvailableModels] = useState<any[]>([])

    useEffect(() => {
        async function load() {
            // Load Survey
            const { data } = await supabase.from("surveys").select("*").eq("id", params.id).single()
            if (data) setSurvey(data)

            // Load Config
            try {
                const res = await fetch("/api/config")
                if (res.ok) {
                    const conf = await res.json()
                    setAvailableModels(conf.available_models)
                }
            } catch (e) {
                console.error("Failed to load config", e)
            }
        }
        load()
    }, [params.id])

    const handleRun = async () => {
        setLoading(true)
        try {
            const { data: { user } } = await supabase.auth.getUser()
            const userId = user?.id || "00000000-0000-0000-0000-000000000000"

            // 1. Create Config Entry
            const constraints: any = {}
            if (demographics.age !== "all") constraints.age = demographics.age
            if (demographics.party !== "all") constraints.party = demographics.party
            if (demographics.custom) constraints.custom_trait = demographics.custom

            const { data: config, error: configError } = await supabase
                .from("demographic_configs")
                .insert({
                    user_id: userId,
                    name: "Custom Run Config",
                    constraints
                })
                .select()
                .single()

            if (configError) throw configError

            // 2. Call Dispatch API
            const res = await fetch("/api/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    surveyId: survey.id,
                    configId: config.id,
                    methodology,
                    userId,
                    modelName
                })
            })

            if (!res.ok) throw new Error("Failed to dispatch")

            const { runId } = await res.json()

            router.push(`/surveys/${survey.id}/results?runId=${runId}`)

        } catch (error) {
            console.error(error)
            alert("Failed to start run")
        } finally {
            setLoading(false)
        }
    }

    if (!survey) return <div>Loading...</div>

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold">Configure Run: {survey.name}</h1>
                <p className="text-muted-foreground">Define your target population.</p>
            </div>

            <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Methodology</label>
                        <select
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            value={methodology}
                            onChange={(e) => setMethodology(e.target.value)}
                        >
                            <option value="DEMOGRAPHIC_FORCING">Demographic Forcing (Standard)</option>
                            <option value="ALTERITY">Alterity Engine (Deep Persona)</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Age Group</label>
                        <select
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            value={demographics.age}
                            onChange={(e) => setDemographics({ ...demographics, age: e.target.value })}
                        >
                            <option value="all">All Ages</option>
                            <option value="18-24">18-24</option>
                            <option value="25-34">25-34</option>
                            <option value="35-44">35-44</option>
                            <option value="45+">45+</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Political Party</label>
                        <select
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            value={demographics.party}
                            onChange={(e) => setDemographics({ ...demographics, party: e.target.value })}
                        >
                            <option value="all">All Parties</option>
                            <option value="Democrat">Democrat</option>
                            <option value="Republican">Republican</option>
                            <option value="Independent">Independent</option>
                        </select>
                    </div>

                    <div className="space-y-2 col-span-2">
                        <label className="text-sm font-medium">Custom Trait (Dynamic Labeling)</label>
                        <input
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            placeholder="e.g. Must own a Tesla, Likes Sci-Fi"
                            value={demographics.custom}
                            onChange={(e) => setDemographics({ ...demographics, custom: e.target.value })}
                        />
                        <p className="text-xs text-muted-foreground">
                            If using Alterity Engine, this will trigger the zero-shot labeler on the backstory pool.
                        </p>
                    </div>

                    <div className="space-y-2 col-span-2">
                        <label className="text-sm font-medium">LLM Model</label>
                        <select
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            value={modelName}
                            onChange={(e) => setModelName(e.target.value)}
                        >
                            {availableModels.length > 0 ? (
                                availableModels.map((m: any) => (
                                    <option key={m.id} value={m.id}>{m.name}</option>
                                ))
                            ) : (
                                <option value="gpt-4-turbo">GPT-4 Turbo (Fallback)</option>
                            )}
                        </select>
                        <p className="text-xs text-muted-foreground">
                            Select the model used for generating responses. (Ensure your worker has access to this model).
                        </p>
                    </div>
                </div>

                <button
                    onClick={handleRun}
                    disabled={loading}
                    className="w-full inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4"
                >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    <Play className="mr-2 h-4 w-4" /> Launch Simulation
                </button>
            </div>
        </div>
    )
}
