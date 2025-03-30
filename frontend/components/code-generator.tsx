"use client"

import { useState, useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Loader2, Key } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent } from "@/components/ui/card"
import { ThemeToggle } from "@/components/theme-toggle"
import { ResultsDisplay } from "@/components/results-display"
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

const models = [
  "llama-3.3-70b-specdec",
  "llama-3.1-8b-instant",
  "llama-3.2-3b-preview",
  "llama-3.1-70b-versatile",
  "llama3-70b-8192",
  "mixtral-8x7b-32768",
  "gemma2-9b-it",
]

const languages = {
  Python: "python",
  Javascript: "javascript",
  "C++": "cpp",
  C: "c",
  Java: "java",
  Ruby: "ruby",
  Rust: "rust",
  R: "r",
  Go: "go",
  Swift: "swift",
  Typescript: "typescript",
  PHP: "php",
}

const formSchema = z.object({
  model: z.string().min(1, "Please select a model"),
  language: z.string().min(1, "Please select a programming language"),
  question: z.string().min(10, "Question must be at least 10 characters"),
  explanation: z.string().optional(),
  userInput: z.string().min(1, "Please provide example input"),
  maxIterations: z.number().min(1).max(5),
})

export function CodeGenerator() {
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [language, setLanguage] = useState("python")
  const [error, setError] = useState("")
  const [apiKey, setApiKey] = useState("")
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false)
  
  useEffect(() => {
    const storedApiKey = localStorage.getItem("groqApiKey")
    if (storedApiKey) {
      setApiKey(storedApiKey)
    }
  }, [])

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      model: "llama-3.3-70b-specdec",
      language: "python",
      question: "",
      explanation: "",
      userInput: "",
      maxIterations: 3,
    },
  })

  const saveApiKey = () => {
    if (!apiKey || apiKey.trim() === "") {
      setError("API key cannot be empty")
      return
    }
    
    localStorage.setItem("groqApiKey", apiKey)
    setError("")
    setIsApiKeyModalOpen(false)
  }

  async function onSubmit(values: z.infer<typeof formSchema>) {
    if (!apiKey) {
      setError("GROQ API key is required. Please add your API key first.")
      setIsApiKeyModalOpen(true)
      return
    }
    
    setIsLoading(true)
    setError("")

    try {
      const payload = {
        model: values.model,
        language: values.language,
        question: values.question,
        explanation: values.explanation || "",
        user_input: values.userInput,
        max_iterations: values.maxIterations,
        api_key: apiKey,
      }

      setLanguage(values.language)

      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/run_pipeline`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      setResults(data.result);
    } catch (err) {
      console.error("Error generating code:", err)
      setError("Failed to generate code. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <div className="flex justify-between mb-2">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => setIsApiKeyModalOpen(true)}
          className="flex items-center gap-2"
        >
          <Key className="h-4 w-4" />
          {apiKey ? "Update API Key" : "Add API Key"}
        </Button>
        <ThemeToggle />
      </div>

      {/* API Key Modal */}
      <Dialog open={isApiKeyModalOpen} onOpenChange={setIsApiKeyModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>GROQ API Key</DialogTitle>
            <DialogDescription>
              Refer to <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" className="text-[#3b82f6] text-[16px] underline">groq console</a> for more details.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <label htmlFor="apiKey" className="text-sm font-medium">API Key</label>
              <Input 
                id="apiKey" 
                type="password" 
                placeholder="Enter your GROQ API key" 
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsApiKeyModalOpen(false)}>Cancel</Button>
            <Button onClick={saveApiKey}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Card>
        <CardContent className="pt-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="model"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Select AI Model</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a model" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {models.map((model) => (
                            <SelectItem key={model} value={model}>
                              {model}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="language"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Select Programming Language</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a language" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {Object.entries(languages).map(([name, value]) => (
                            <SelectItem key={value} value={value}>
                              {name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="question"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Programming Question</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Describe the problem statement in detail..."
                        className="min-h-[120px] font-mono"
                        {...field}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="explanation"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Explanation (Optional)</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Explain the problem for better context..."
                        className="min-h-[80px] font-mono"
                        {...field}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="userInput"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>User Input Example</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Example user input (space-separated values)"
                        className="font-mono"
                        {...field}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="maxIterations"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Max Iterations: {field.value}</FormLabel>
                    <FormControl>
                      <Slider
                        min={1}
                        max={5}
                        step={1}
                        defaultValue={[field.value]}
                        onValueChange={(vals) => field.onChange(vals[0])}
                      />
                    </FormControl>
                    <FormDescription>Maximum number of code generation attempts (1-5)</FormDescription>
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Code...
                  </>
                ) : (
                  "Generate Code"
                )}
              </Button>

              {error && (
                <div className="p-4 bg-red-500/20 text-red-600 dark:text-red-400 rounded-md">
                  {error}
                </div>
              )}        
             </form>
          </Form>
        </CardContent>
      </Card>

      {results && <ResultsDisplay results={results} language={language} />}
    </div>
  )
}
