import Link from "next/link"
import { Circle, User, Menu } from "lucide-react"

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 hidden md:flex">
            <Link className="mr-6 flex items-center space-x-2" href="/">
              <Circle className="h-6 w-6" />
              <span className="hidden font-bold sm:inline-block">Alterity</span>
            </Link>
            <nav className="flex items-center space-x-6 text-sm font-medium">
              <Link href="/surveys/new">New Survey</Link>
              <Link href="/surveys">Dashboard</Link>
            </nav>
          </div>
          <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
            <div className="w-full flex-1 md:w-auto md:flex-none">
              {/* Search or extra tools */}
            </div>
            <nav className="flex items-center">
              <button className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center">
                <User className="h-4 w-4" />
              </button>
            </nav>
          </div>
        </div>
      </header>
      <main className="flex-1 container py-6">
        {children}
      </main>
    </div>
  )
}
