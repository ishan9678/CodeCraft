"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent } from "@/components/ui/card"
import { ThemeToggle } from "@/components/theme-toggle"
import { ResultsDisplay } from "@/components/results-display"

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
  const [error, setError] = useState("")

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

  async function onSubmit(values: z.infer<typeof formSchema>) {
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
      }

      console.log("Payload to send:", payload)

      const response = await fetch("http://127.0.0.1:8000/run_pipeline", {
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
    <div >
      <div className="flex justify-end mb-2">
        <ThemeToggle />
      </div>

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

              {error && <div className="p-4 bg-destructive/15 text-destructive rounded-md">{error}</div>}
            </form>
          </Form>
        </CardContent>
      </Card>

      {results && <ResultsDisplay results={results} />}
    </div>
  )
}

// Mock response generator for demonstration
function getMockResponse(language: string) {
  const codeSnippet =
    language === "python"
      ? `def max_subarray_sum(arr):
    max_so_far = float('-inf')
    max_ending_here = 0
    
    for num in arr:
        max_ending_here = max(num, max_ending_here + num)
        max_so_far = max(max_so_far, max_ending_here)
        
    return max_so_far`
      : `function maxSubarraySum(arr) {
  let maxSoFar = -Infinity;
  let maxEndingHere = 0;
  
  for (let i = 0; i < arr.length; i++) {
    maxEndingHere = Math.max(arr[i], maxEndingHere + arr[i]);
    maxSoFar = Math.max(maxSoFar, maxEndingHere);
  }
  
  return maxSoFar;
}`

  return {
    cot: [
      "Step 1: Understanding the problem - We need to find the contiguous subarray with the largest sum.",
      "Step 2: Identifying edge cases - We need to handle arrays with all negative numbers and empty arrays.",
      "Step 3: Implementing a solution using Kadane's Algorithm which has O(n) time complexity.",
      "Step 4: Running tests and refining the implementation to ensure correctness.",
    ],
    final_code: codeSnippet,
    final_result: {
      output: "7",
      time: "0.02",
      memory: 3200,
      stderror: "",
      compiler_errors: "",
    },
    test_results: [
      {
        input: "-2 -3 4 -1 -2 1 5 -3",
        expected_output: "7",
        actual_output: "7",
        stderror: "",
        compiler_errors: "",
        time: "0.02",
        memory: 3200,
        passed: true,
      },
    ],
    iterations: 2,
    history: [
      {
        iteration: 1,
        chain_of_thought: [
          "Step 1: Initial approach - I'll implement a basic version of Kadane's algorithm.",
          "Step 2: Implementing basic logic - Track current sum and maximum sum seen so far.",
        ],
        code:
          language === "python"
            ? `def max_subarray_sum(arr):
    max_sum = 0
    current_sum = 0
    
    for num in arr:
        current_sum += num
        if current_sum < 0:
            current_sum = 0
        max_sum = max(max_sum, current_sum)
        
    return max_sum`
            : `function maxSubarraySum(arr) {
  let maxSum = 0;
  let currentSum = 0;
  
  for (let i = 0; i < arr.length; i++) {
    currentSum += arr[i];
    if (currentSum < 0) {
      currentSum = 0;
    }
    maxSum = Math.max(maxSum, currentSum);
  }
  
  return maxSum;
}`,
        execution_result: {
          output: "5",
          time: "0.03",
          memory: 3300,
          stderror: "",
          compiler_errors: "",
        },
        test_results: [
          {
            input: "-2 -3 4 -1 -2 1 5 -3",
            expected_output: "7",
            actual_output: "5",
            passed: false,
          },
        ],
      },
      {
        iteration: 2,
        chain_of_thought: [
          "Step 1: Fixing the edge cases - The previous implementation doesn't handle all-negative arrays correctly.",
          "Step 2: Optimizing the algorithm - Updating the logic to handle negative numbers properly.",
        ],
        code: codeSnippet,
        execution_result: {
          output: "7",
          time: "0.025",
          memory: 3250,
          stderror: "",
          compiler_errors: "",
        },
        test_results: [
          {
            input: "-2 -3 4 -1 -2 1 5 -3",
            expected_output: "7",
            actual_output: "7",
            passed: true,
          },
        ],
      },
    ],
    success: true,
  }
}

