"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/lib/supabase"
import { Loader2, RefreshCw } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function ResultsPage({ params, searchParams }: { params: { id: string }, searchParams: { runId: string } }) {
    const supabase = createClient()
    const [results, setResults] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [stats, setStats] = useState<any[]>([])

    const runId = searchParams.runId

    useEffect(() => {
        // Initial Load
        fetchResults()

        // Realtime Subscription
        const channel = supabase
            .channel('results_changes')
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'public',
                    table: 'results',
                    filter: runId ? `run_id=eq.${runId}` : undefined
                },
                (payload) => {
                    // New result came in
                    setResults((prev) => [...prev, payload.new])
                }
            )
            .subscribe()

        return () => {
            supabase.removeChannel(channel)
        }
    }, [runId])

    // Update stats when results change
    useEffect(() => {
        if (results.length === 0) return

        // Simple Sentiment Analysis / Distribution Logic
        // For now, let's just group by political party if available in response, OR just count tokens/length?
        // Since response is text, we can't chart it easily without parsing.
        // Let's assume response might have a sentiment classification in a real app.
        // For this visualization, let's chart "Response Length" distribution as a proxy for "Effort/Depth"

        // OR, if we had multiple choices questions, we'd chart selections.
        // Let's assume just a list view for open ended is fine, and maybe a chart of "Responses per Probe"

        const probeCounts: any = {}
        results.forEach(r => {
            const pid = r.probe_id
            probeCounts[pid] = (probeCounts[pid] || 0) + 1
        })

        const chartData = Object.keys(probeCounts).map(pid => ({
            name: `Probe ${pid}`,
            count: probeCounts[pid]
        }))
        setStats(chartData)

    }, [results])

    async function fetchResults() {
        if (!runId) return
        setLoading(true)
        const { data } = await supabase
            .from("results")
            .select(`
            *,
            backstory:backstories(model_signature, demographics)
        `)
            .eq("run_id", runId)
            .order("created_at", { ascending: false })

        if (data) {
            setResults(data)
        }
        setLoading(false)
    }

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Simulation Results</h1>
                    <p className="text-muted-foreground">Run ID: {runId} • {results.length} Responses</p>
                </div>
                <button onClick={fetchResults} className="p-2 hover:bg-slate-100 rounded-full">
                    <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Chart Section */}
                {/* Chart Section */}
                <div className="md:col-span-3 lg:col-span-2 h-[300px] bg-card border rounded-xl p-4 shadow-sm flex gap-4">
                    <div className="flex-1">
                        <h3 className="text-sm font-semibold mb-4">Response Volume per Probe</h3>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={stats}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px' }} />
                                <Bar dataKey="count" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    {/* Placeholder for Sentiment or other metrics */}
                    <div className="w-1/3 border-l pl-4 hidden md:block">
                        <h3 className="text-sm font-semibold mb-4">Estimated Sentiment</h3>
                        <div className="flex items-center justify-center h-full pb-8 text-muted-foreground text-sm italic">
                            (Requires NLP Module)
                        </div>
                    </div>
                </div>

                {/* Stats Card */}
                <div className="bg-card border rounded-xl p-4 shadow-sm space-y-4">
                    <h3 className="text-sm font-semibold">Run Stats</h3>
                    <div className="text-2xl font-bold">{results.length}</div>
                    <p className="text-xs text-muted-foreground">Total Responses Generated</p>
                    <div className="h-px bg-border" />
                    <div className="text-2xl font-bold">
                        ${results.reduce((acc, curr) => acc + (curr.usage_cost || 0), 0).toFixed(4)}
                    </div>
                    <p className="text-xs text-muted-foreground">Estimated Cost</p>
                </div>
            </div>

            <div className="space-y-4">
                <h3 className="text-lg font-semibold">Live Feed</h3>
                <div className="grid gap-4">
                    {results.map((result) => (
                        <div key={result.id} className="bg-card border rounded-lg p-4 shadow-sm transition-all hover:border-primary/50">
                            <div className="flex justify-between items-start mb-2">
                                <div className="flex gap-2">
                                    {result.backstory?.demographics && (
                                        <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                            {result.backstory.demographics.age} • {result.backstory.demographics.political_party}
                                        </span>
                                    )}
                                    <span className="text-xs text-muted-foreground self-center">
                                        Probe #{result.probe_id}
                                    </span>
                                </div>
                                <span className="text-xs text-muted-foreground">
                                    {new Date(result.created_at).toLocaleTimeString()}
                                </span>
                            </div>
                            <p className="text-sm leading-relaxed">
                                {result.response?.text || JSON.stringify(result.response)}
                            </p>
                        </div>
                    ))}
                    {results.length === 0 && !loading && (
                        <div className="text-center py-12 text-muted-foreground">
                            Waiting for results...
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
