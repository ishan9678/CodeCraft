"use client"

import { useState, useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Loader2, Key, Info, PlusCircle, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent } from "@/components/ui/card"
import { ThemeToggle } from "@/components/theme-toggle"
import { ResultsDisplay } from "@/components/results-display"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

const providers = {
  groq: {
    name: "GROQ",
    apiUrl: "https://console.groq.com/keys",
    models: [
      "llama-3.3-70b-versatile",
      "meta-llama/llama-4-maverick-17b-128e-instruct",
      "meta-llama/llama-4-scout-17b-16e-instruct",
      "llama-3.1-8b-instant",
      "llama-3.2-3b-preview",
      "llama-3.1-70b-versatile",
      "llama3-70b-8192",
      "mixtral-8x7b-32768",
      "gemma2-9b-it",
    ]
  },
  sambanova: {
    name: "SambaNova",
    apiUrl: "https://cloud.sambanova.ai/",
    models: [
      "Llama-4-Maverick-17B-128E-Instruct",
      "Llama-4-Scout-17B-16E-Instruct",
      "Meta-Llama-3.3-70B-Instruct",
    ]
  },
}

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
  provider: z.string().min(1, "Please select a provider"),
  model: z.string().min(1, "Please select a model"),
  language: z.string().min(1, "Please select a programming language"),
  question: z.string().min(10, "Question must be at least 10 characters"),
  questionCode: z.string().optional(),
  explanation: z.string().optional(),
  userInput: z.string().min(1, "Please provide example input"),
  maxIterations: z.number().min(1).max(5),
  generateTestCases: z.boolean(),
  manualTestCases: z.array(
    z.object({
      input: z.string().min(1, "Input cannot be empty"),
      expected_output: z.string().min(1, "Expected output cannot be empty")
    })
  ).optional(),
})

// Define type based on schema
type FormValues = z.infer<typeof formSchema>;

export function CodeGenerator() {
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [language, setLanguage] = useState("python")
  const [error, setError] = useState("")
  const [apiKey, setApiKey] = useState("")
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false)
  const [showQuestionCode, setShowQuestionCode] = useState(false)
  const [lastShiftPressTime, setLastShiftPressTime] = useState(0)
  const [selectedProvider, setSelectedProvider] = useState<keyof typeof providers>("groq")
  const [manualTestCaseError, setManualTestCaseError] = useState("");

  useEffect(() => {
    const storedApiKey = localStorage.getItem(`${selectedProvider}ApiKey`)
    if (storedApiKey) {
      setApiKey(storedApiKey)
    } else {
      setApiKey("")
    }

    // Set up event listener for shift key
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Shift') {
        const currentTime = Date.now();
        if (currentTime - lastShiftPressTime < 500) { // 500ms threshold for double press
          setShowQuestionCode(true);
        }
        setLastShiftPressTime(currentTime);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [lastShiftPressTime, selectedProvider]);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      provider: "groq",
      model: "llama-3.3-70b-versatile",
      language: "python",
      question: "",
      questionCode: "",
      explanation: "",
      userInput: "",
      maxIterations: 3,
      generateTestCases: true,
      manualTestCases: [{ input: "", expected_output: "" }],
    },
  })

  // Update model when provider changes
  useEffect(() => {
    const currentModel = form.getValues("model");
    const availableModels = providers[selectedProvider].models;
    
    // Reset model if current model is not available in new provider
    if (!availableModels.includes(currentModel)) {
      form.setValue("model", availableModels[0]);
    }
    
    form.setValue("provider", selectedProvider);
  }, [selectedProvider, form]);

  const handleProviderChange = (value: keyof typeof providers) => {
    setSelectedProvider(value);
  };

  const saveApiKey = () => {
    if (!apiKey || apiKey.trim() === "") {
      setError("API key cannot be empty")
      return
    }

    localStorage.setItem(`${selectedProvider}ApiKey`, apiKey)
    setError("")
    setIsApiKeyModalOpen(false)
  }

  const addTestCase = () => {
    const currentTestCases = form.getValues("manualTestCases") || [];
    form.setValue("manualTestCases", [...currentTestCases, { input: "", expected_output: "" }]);
  };

  const removeTestCase = (index: number) => {
    const currentTestCases = form.getValues("manualTestCases") || [];
    if (currentTestCases.length > 1) {
      form.setValue("manualTestCases", currentTestCases.filter((_, i) => i !== index));
    } else {
      setManualTestCaseError("At least one test case is required");
    }
  };

  useEffect(() => {
    const subscription = form.watch((value) => {
      if (!value.generateTestCases && (!value.manualTestCases || value.manualTestCases.length === 0)) {
        form.setValue("manualTestCases", [{ input: "", expected_output: "" }]);
      }
    });
    return () => subscription.unsubscribe();
  }, [form]);

  async function onSubmit(values: FormValues) {
    if (!apiKey) {
      setError(`${providers[selectedProvider].name} API key is required. Please add your API key first.`)
      setIsApiKeyModalOpen(true)
      return
    }

    setIsLoading(true)
    setError("")

    try {
      const testCases = values.generateTestCases ? [] : values.manualTestCases?.map(tc => ({
        input: tc.input,
        expected_output: tc.expected_output
      })) || [];

      const payload = {
        provider: values.provider,
        model: values.model,
        language: values.language,
        question: values.question,
        question_code: values.questionCode || "",
        explanation: values.explanation || "",
        user_input: values.userInput,
        max_iterations: values.maxIterations,
        generate_test_cases: values.generateTestCases,
        test_cases: testCases,
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
        <div className="flex items-center gap-2">
          <Select value={selectedProvider} onValueChange={handleProviderChange}>
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent>
              {Object.keys(providers).map((key) => (
                <SelectItem key={key} value={key}>
                  {providers[key as keyof typeof providers].name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsApiKeyModalOpen(true)}
            className="flex items-center gap-2"
          >
            <Key className="h-4 w-4" />
            {apiKey ? "Update API Key" : "Add API Key"}
          </Button>
        </div>
        <ThemeToggle />
      </div>

      {/* API Key Modal */}
      <Dialog open={isApiKeyModalOpen} onOpenChange={setIsApiKeyModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{providers[selectedProvider].name} API Key</DialogTitle>
            <DialogDescription>
              Refer to <a href={providers[selectedProvider].apiUrl} target="_blank" rel="noopener noreferrer" className="text-[#3b82f6] text-[16px] underline">{providers[selectedProvider].name} console</a> for more details.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <label htmlFor="apiKey" className="text-sm font-medium">API Key</label>
              <Input
                id="apiKey"
                type="password"
                placeholder={`Enter your ${providers[selectedProvider].name} API key`}
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
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a model" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {providers[selectedProvider].models.map((model) => (
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

              {showQuestionCode && (
                <FormField
                  control={form.control}
                  name="questionCode"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Question Code (Optional)</FormLabel>
                      <FormControl>
                        <Input
                          placeholder=""
                          className="font-mono"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        Only for internal use, please ignore this field.
                      </FormDescription>
                    </FormItem>
                  )}
                />
              )}

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
                      <Textarea
                        placeholder="Example user input (supports multiple lines)"
                        className="min-h-[80px] font-mono"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>Enter example inputs, supports newlines</FormDescription>
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

              <FormField
                control={form.control}
                name="generateTestCases"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox 
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Auto-generate test cases
                      </FormLabel>
                      <FormDescription>
                        Let AI create test cases for your code
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />

              {/* Manual Test Case Fields */}
              {!form.watch("generateTestCases") && (
                <div className="space-y-4 p-4 border rounded-md">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Manual Test Cases</h3>
                    <Button 
                      type="button" 
                      variant="outline" 
                      size="sm"
                      onClick={addTestCase}
                      className="flex items-center gap-1"
                    >
                      <PlusCircle className="h-4 w-4" />
                      Add Test Case
                    </Button>
                  </div>
                  
                  {manualTestCaseError && (
                    <div className="p-2 text-sm bg-red-500/10 text-red-600 dark:text-red-400 rounded-md">
                      {manualTestCaseError}
                    </div>
                  )}
                  
                  {form.watch("manualTestCases")?.map((_, index) => (
                    <div key={index} className="p-3 border rounded-md space-y-3">
                      <div className="flex justify-between items-start">
                        <span className="font-medium">Test Case {index + 1}</span>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm" 
                          onClick={() => removeTestCase(index)}
                          className="h-8 w-8 p-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      <FormField
                        control={form.control}
                        name={`manualTestCases.${index}.input`}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Input</FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder="Test case input"
                                className="font-mono"
                                {...field}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name={`manualTestCases.${index}.expected_output`}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Expected Output</FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder="Expected output"
                                className="font-mono"
                                {...field}
                              />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                    </div>
                  ))}
                </div>
              )}

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
