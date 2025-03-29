import { CodeGenerator } from "@/components/code-generator"

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8 lg:p-12">
      <div className="max-w-7xl mx-auto">
        <header className="mb-4">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Code Craft</h1>
          <p className="text-muted-foreground mt-2">Generate optimized code solutions through iterative refinement</p>
        </header>
        <CodeGenerator />
      </div>
    </main>
  )
}

