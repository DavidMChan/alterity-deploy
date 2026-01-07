"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase"
import { Loader2, Plus, Trash2 } from "lucide-react"

export default function NewSurveyPage() {
    const router = useRouter()
    const supabase = createClient()

    const [loading, setLoading] = useState(false)
    const [name, setName] = useState("")
    const [probes, setProbes] = useState([""])

    const addProbe = () => setProbes([...probes, ""])
    const updateProbe = (index: number, value: string) => {
        const newProbes = [...probes]
        newProbes[index] = value
        setProbes(newProbes)
    }
    const removeProbe = (index: number) => {
        setProbes(probes.filter((_, i) => i !== index))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            // 1. Create Survey
            // Ideally we get user.id from auth context, assuming mocked/anon for now or handling in RLS
            const { data: { user } } = await supabase.auth.getUser()

            // If no user, we might fail RLS, but for prototype we assume anon key works or local dev
            // For now, let's insert a dummy user_id or rely on RLS if authenticated

            const { data: survey, error: surveyError } = await supabase
                .from("surveys")
                .insert({
                    name,
                    user_id: user?.id || "00000000-0000-0000-0000-000000000000", // Fallback for dev without auth flow
                    status: "draft"
                })
                .select()
                .single()

            if (surveyError) throw surveyError

            // 2. Insert Probes
            const probesData = probes
                .filter(p => p.trim().length > 0)
                .map((p, i) => ({
                    survey_id: survey.id,
                    content: p,
                    order_index: i,
                    type: "open_ended"
                }))

            if (probesData.length > 0) {
                const { error: probeError } = await supabase
                    .from("probes")
                    .insert(probesData)
                if (probeError) throw probeError
            }

            router.push(`/surveys/${survey.id}/run`)
        } catch (error) {
            console.error(error)
            alert("Error creating survey")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold">New Survey</h1>
                <p className="text-muted-foreground">Define your research questions.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                    <label className="text-sm font-medium">Survey Name</label>
                    <input
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                        placeholder="e.g. Political Pulse Check"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>

                <div className="space-y-4">
                    <label className="text-sm font-medium">Probes (Questions)</label>
                    {probes.map((probe, index) => (
                        <div key={index} className="flex gap-2">
                            <input
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                placeholder="What is your opinion on..."
                                value={probe}
                                onChange={(e) => updateProbe(index, e.target.value)}
                                required
                            />
                            {probes.length > 1 && (
                                <button
                                    type="button"
                                    onClick={() => removeProbe(index)}
                                    className="p-2 text-destructive hover:bg-destructive/10 rounded-md"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </button>
                            )}
                        </div>
                    ))}
                    <button
                        type="button"
                        onClick={addProbe}
                        className="flex items-center text-sm text-primary hover:underline"
                    >
                        <Plus className="h-4 w-4 mr-1" /> Add Question
                    </button>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4"
                >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Continue to Configuration
                </button>
            </form>
        </div>
    )
}
