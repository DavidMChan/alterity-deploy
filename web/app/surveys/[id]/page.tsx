"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/lib/supabase"
import Link from "next/link"
import { ArrowLeft, Edit2, Play, Save } from "lucide-react"

export default function SurveyDetailsPage({ params }: { params: { id: string } }) {
    const supabase = createClient()
    const [survey, setSurvey] = useState<any>(null)
    const [probes, setProbes] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [runs, setRuns] = useState<any[]>([])

    // Edit Mode
    const [isEditing, setIsEditing] = useState(false)
    const [editedName, setEditedName] = useState("")

    useEffect(() => {
        loadData()
    }, [params.id])

    async function loadData() {
        setLoading(true)
        // Load Survey
        const { data: s } = await supabase.from("surveys").select("*").eq("id", params.id).single()
        if (s) {
            setSurvey(s)
            setEditedName(s.name)
        }

        // Load Probes
        const { data: p } = await supabase.from("probes").select("*").eq("survey_id", params.id).order("id")
        if (p) setProbes(p)

        // Load Runs History
        const { data: r } = await supabase.from("survey_runs").select("*").eq("survey_id", params.id).order("created_at", { ascending: false })
        if (r) setRuns(r)

        setLoading(false)
    }

    async function saveChanges() {
        if (!survey) return
        await supabase.from("surveys").update({ name: editedName }).eq("id", survey.id)
        setIsEditing(false)
        loadData()
    }

    if (loading) return <div>Loading...</div>
    if (!survey) return <div>Survey not found</div>

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <Link href="/surveys" className="text-sm text-muted-foreground hover:text-foreground flex items-center">
                <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
            </Link>

            {/* Header */}
            <div className="flex justify-between items-start">
                <div className="space-y-1">
                    {isEditing ? (
                        <input
                            className="text-3xl font-bold bg-transparent border-b border-primary focus:outline-none"
                            value={editedName}
                            onChange={(e) => setEditedName(e.target.value)}
                        />
                    ) : (
                        <h1 className="text-3xl font-bold">{survey.name}</h1>
                    )}
                    <div className="text-sm text-muted-foreground">ID: {survey.id} • Status: {survey.status}</div>
                </div>
                <div className="flex gap-2">
                    {isEditing ? (
                        <button onClick={saveChanges} className="btn-primary flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md">
                            <Save className="h-4 w-4" /> Save
                        </button>
                    ) : (
                        <button onClick={() => setIsEditing(true)} className="btn-secondary flex items-center gap-2 border px-4 py-2 rounded-md hover:bg-slate-50">
                            <Edit2 className="h-4 w-4" /> Edit
                        </button>
                    )}
                    <Link
                        href={`/surveys/${survey.id}/run`}
                        className="btn-primary flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
                    >
                        <Play className="h-4 w-4" /> Run New Simulation
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Left Column: Probes */}
                <div className="md:col-span-2 space-y-6">
                    <div className="bg-card border rounded-lg p-6 shadow-sm">
                        <h2 className="text-xl font-semibold mb-4">Probes</h2>
                        <div className="space-y-4">
                            {probes.map((probe, i) => (
                                <div key={probe.id} className="p-4 bg-muted/50 rounded-md border text-sm">
                                    <div className="font-medium mb-1">Q{i + 1}</div>
                                    <p>{probe.content}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: History */}
                <div className="space-y-6">
                    <div className="bg-card border rounded-lg p-6 shadow-sm">
                        <h2 className="text-xl font-semibold mb-4">Run History</h2>
                        {runs.length === 0 ? (
                            <p className="text-muted-foreground text-sm">No runs yet.</p>
                        ) : (
                            <div className="space-y-3">
                                {runs.map(run => (
                                    <Link key={run.id} href={`/surveys/${survey.id}/results?runId=${run.id}`} className="block">
                                        <div className="p-3 border rounded-md hover:bg-slate-50 transition-colors">
                                            <div className="flex justify-between items-center mb-1">
                                                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${run.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
                                                        run.status === 'FAILED' ? 'bg-red-100 text-red-700' :
                                                            'bg-blue-100 text-blue-700'
                                                    }`}>
                                                    {run.status}
                                                </span>
                                                <span className="text-xs text-muted-foreground">Run #{run.id}</span>
                                            </div>
                                            <div className="text-sm font-medium truncate">{run.methodology}</div>
                                            <div className="text-xs text-muted-foreground mt-1">
                                                {new Date(run.created_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
