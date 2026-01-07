"use client"

import { useState } from "react"
import { Save } from "lucide-react"

export default function SettingsPage() {
    const [apiKey, setApiKey] = useState("")

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold">Settings</h1>
                <p className="text-muted-foreground">Manage your API keys and defaults.</p>
            </div>

            <div className="bg-card border rounded-lg p-6 space-y-6 shadow-sm">
                <div>
                    <h2 className="text-lg font-semibold mb-1">Backend Configuration</h2>
                    <p className="text-sm text-muted-foreground">Configure the connection to the Alterity Worker.</p>
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-medium">OpenAI API Key (Optional Override)</label>
                    <input
                        type="password"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        placeholder="sk-..."
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">
                        If provided, the worker can use this key for your specific runs (BYOD).
                        Currently, the worker uses the system environment variable.
                    </p>
                </div>

                <div className="pt-4">
                    <button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4">
                        <Save className="mr-2 h-4 w-4" /> Save Settings
                    </button>
                </div>
            </div>
        </div>
    )
}
