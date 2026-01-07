"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { createClient } from "@/lib/supabase"
import { Plus, Trash2, ArrowRight, BarChart2, Play } from "lucide-react"

export default function SurveysPage() {
    const supabase = createClient()
    const [surveys, setSurveys] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadSurveys()
    }, [])

    async function loadSurveys() {
        setLoading(true)
        const { data } = await supabase
            .from("surveys")
            .select("*")
            .order("created_at", { ascending: false })
        //.eq("user_id", ...) // If auth is enabled

        if (data) setSurveys(data)
        setLoading(false)
    }

    async function deleteSurvey(id: number) {
        if (!confirm("Are you sure? This will delete all runs and results.")) return

        const { error } = await supabase.from("surveys").delete().eq("id", id)
        if (error) {
            alert("Error deleting survey")
        } else {
            loadSurveys()
        }
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Surveys</h1>
                    <p className="text-muted-foreground">Manage your research projects.</p>
                </div>
                <Link
                    href="/surveys/new"
                    className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4 shadow-sm"
                >
                    <Plus className="mr-2 h-4 w-4" /> New Survey
                </Link>
            </div>

            {loading ? (
                <div className="py-12 text-center text-muted-foreground">Loading...</div>
            ) : surveys.length === 0 ? (
                <div className="py-20 text-center border rounded-xl bg-slate-50">
                    <h3 className="text-lg font-semibold">No surveys yet</h3>
                    <p className="text-muted-foreground mb-4">Create your first demographic simulation.</p>
                    <Link
                        href="/surveys/new"
                        className="text-primary hover:underline"
                    >
                        Get Started &rarr;
                    </Link>
                </div>
            ) : (
                <div className="grid gap-4">
                    {surveys.map((survey) => (
                        <div key={survey.id} className="group bg-card border rounded-lg p-5 flex items-center justify-between hover:shadow-md transition-all">
                            <div className="space-y-1">
                                <Link href={`/surveys/${survey.id}`} className="font-semibold text-lg hover:underline decoration-primary/50 underline-offset-4">
                                    {survey.name}
                                </Link>
                                <div className="flex gap-2 text-xs text-muted-foreground">
                                    <span className="capitalize bg-slate-100 px-2 py-0.5 rounded-full">{survey.status}</span>
                                    <span>•</span>
                                    <span>Created {new Date(survey.created_at || Date.now()).toLocaleDateString()}</span>
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <Link
                                    href={`/surveys/${survey.id}/run`}
                                    className="p-2 text-muted-foreground hover:text-foreground hover:bg-slate-100 rounded-md tooltip-trigger"
                                    title="Run Simulation"
                                >
                                    <Play className="h-4 w-4" />
                                </Link>
                                <Link
                                    href={`/surveys/${survey.id}/results`}
                                    className="p-2 text-muted-foreground hover:text-foreground hover:bg-slate-100 rounded-md"
                                    title="View Results"
                                >
                                    <BarChart2 className="h-4 w-4" />
                                </Link>
                                <div className="w-px h-4 bg-border mx-1" />
                                <button
                                    onClick={() => deleteSurvey(survey.id)}
                                    className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md"
                                    title="Delete"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </button>
                                <Link
                                    href={`/surveys/${survey.id}`}
                                    className="p-2 text-muted-foreground hover:text-foreground hover:bg-slate-100 rounded-md"
                                >
                                    <ArrowRight className="h-4 w-4" />
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
