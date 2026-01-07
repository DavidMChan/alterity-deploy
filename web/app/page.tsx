import Link from "next/link"

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 text-center">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
        Demographic Simulation Engine
      </h1>
      <p className="text-xl text-muted-foreground w-full max-w-2xl">
        Simulate survey responses from millions of realistic AI personas.
        Use "Alterity" engine for deep backstory grounding, or standard demographic forcing.
      </p>

      <div className="flex gap-4 pt-4">
        <Link
          href="/surveys/new"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4"
        >
          Create Survey
        </Link>
        <Link
          href="/surveys"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background border border-input hover:bg-accent hover:text-accent-foreground h-10 py-2 px-4"
        >
          View Existing
        </Link>
      </div>
    </div>
  )
}
