"use client"

import { useState } from "react"
import { Check, Copy, Clock, HardDrive } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface TestResult {
  input: string
  expected_output: string
  actual_output: string
  passed: boolean
  stderror?: string
  compiler_errors?: string
  time?: string
  memory?: number
}

interface IterationResult {
  iteration: number
  chain_of_thought: string[]
  code: string
  execution_result: {
    output: string
    time: string
    memory: number
    stderror: string
    compiler_errors: string
  }
  test_results: TestResult[]
}

interface ResultsProps {
  results: {
    cot: string[]
    final_code: string
    final_result: {
      output: string
      time: string
      memory: number
      stderror: string
      compiler_errors: string
    }
    test_results: TestResult[]
    iterations: number
    history: IterationResult[]
    success: boolean
  }
}

export function ResultsDisplay({ results, language }: ResultsProps & { language: string }) {
  const [copied, setCopied] = useState(false)
  const { theme, resolvedTheme } = useTheme()
  const currentTheme = theme === "system" ? resolvedTheme : theme

  const copyToClipboard = () => {
    navigator.clipboard.writeText(results.final_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Results</span>
          <Badge
            variant={results.success ? "default" : "destructive"}
            className={
              results.success
                ? "bg-green-100 text-green-800 hover:bg-green-200"
                : "bg-red-100 text-red-800 hover:bg-red-200"
            }
          >
            {results.success ? "Success" : "Failed"}
          </Badge>
        </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
        <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-600">Reasoning Process</h3>
            <div className="border rounded-lg overflow-hidden">
              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="cot">
                  <AccordionTrigger className="px-4 py-3 transition-colors">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">Model's Thought Process</span>
                      {/* Loading dots animation */}
                      <div className="flex space-x-1">
                        <div className="h-1 w-1 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
                        <div className="h-1 w-1 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
                        <div className="h-1 w-1 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent 
                    className={`px-4 py-3 ${currentTheme === "dark" ? "bg-[#27272a] border-t border-gray-700" : "bg-gray-100 border-t border-gray-200"}`}
                  >
                    <ol className="space-y-3">
                      {results.cot.map((step, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-xs text-gray-500 mr-2 mt-[2.5px]">{index + 1}.</span>
                          <span className={`text-sm ${currentTheme === "dark" ? "text-gray-300" : "text-gray-800"} `}>{step}</span>
                        </li>
                      ))}
                    </ol>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-medium">Final Generated Code</h3>
              <Button variant="outline" size="sm" onClick={copyToClipboard} className="flex items-center gap-1">
                {copied ? (
                  <>
                    <Check className="h-4 w-4" />
                    <span>Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    <span>Copy Code</span>
                  </>
                )}
              </Button>
            </div>
            <div className="relative rounded-md bg-muted p-4 overflow-x-auto">
              <SyntaxHighlighter
                  language={language}
                  style={oneDark}
                  className="text-sm rounded-md font-mono"
                  customStyle={{
                    background: "transparent",
                    padding: "0", 
                    margin: "0", 
                    fontSize: "0.875rem", 
                    whiteSpace: "pre-wrap",
                  }}
                  showLineNumbers
                  wrapLongLines
                >
                  {results.final_code}
                </SyntaxHighlighter>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Final Execution Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4 flex items-center gap-2">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Execution Time</p>
                    <p className="font-medium">{results.final_result.time}s</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-2">
                  <HardDrive className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Memory Usage</p>
                    <p className="font-medium">{results.final_result.memory} KB</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground">Output</p>
                  <p className="font-mono">{results.final_result.output}</p>
                </CardContent>
              </Card>
            </div>
            {(results.final_result.stderror || results.final_result.compiler_errors) && (
              <div className="mt-4 p-4 bg-destructive/15 text-destructive rounded-md">
                <p className="font-medium">Errors:</p>
                <pre className="text-sm mt-2 whitespace-pre-wrap font-mono">
                  {results.final_result.stderror || results.final_result.compiler_errors}
                </pre>
              </div>
            )}
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Test Results</h3>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Input</TableHead>
                    <TableHead>Expected Output</TableHead>
                    <TableHead>Actual Output</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.test_results.map((test, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-mono whitespace-pre-wrap">{test.input}</TableCell>
                      <TableCell className="font-mono whitespace-pre-wrap">{test.expected_output}</TableCell>
                      <TableCell className="font-mono whitespace-pre-wrap">{test.actual_output}</TableCell>
                      <TableCell>
                        {test.passed ? (
                          <Badge variant="secondary" className="bg-green-100 text-green-800 hover:bg-green-100">
                            Passed
                          </Badge>
                        ) : (
                          <Badge variant="destructive">Failed</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Iteration History</h3>
            <Tabs defaultValue="1">
              <TabsList className="mb-4">
                {results.history.map((iteration) => (
                  <TabsTrigger key={iteration.iteration} value={iteration.iteration.toString()}>
                    Iteration {iteration.iteration}
                  </TabsTrigger>
                ))}
              </TabsList>
              {results.history.map((iteration) => (
                <TabsContent key={iteration.iteration} value={iteration.iteration.toString()}>
                  <Card>
                    <CardContent className="p-4 space-y-4">
                      <div>
                          <h4 className="font-medium mb-2">Reasoning</h4>
                          <ol className="space-y-3">
                            {iteration.chain_of_thought.map((step, index) => (
                            <li key={index} className="flex pl-1 items-start">
                                <span className="text-xs text-muted-foreground mr-2 mt-[2.5px]">{index + 1}.</span>
                                <span className={`text-sm ${currentTheme === "dark" ? "text-gray-300" : "text-gray-800"} `}>{step}</span>
                            </li>
                            ))}
                          </ol>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Code</h4>
                        <div className="relative rounded-md bg-muted p-4 overflow-x-auto">
                          <SyntaxHighlighter
                            language={language}
                            style={oneDark}
                            className="text-sm rounded-md font-mono"
                            customStyle={{
                              background: "transparent",
                              padding: "0", 
                              margin: "0", 
                              fontSize: "0.875rem", 
                              whiteSpace: "pre-wrap",
                            }}
                            showLineNumbers
                            wrapLongLines
                          >
                            {iteration.code}
                          </SyntaxHighlighter>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Execution Results</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <Card>
                            <CardContent className="p-4 flex items-center gap-2">
                              <Clock className="h-5 w-5 text-muted-foreground" />
                              <div>
                                <p className="text-sm text-muted-foreground">Execution Time</p>
                                <p className="font-medium">{iteration.execution_result.time}s</p>
                              </div>
                            </CardContent>
                          </Card>
                          <Card>
                            <CardContent className="p-4 flex items-center gap-2">
                              <HardDrive className="h-5 w-5 text-muted-foreground" />
                              <div>
                                <p className="text-sm text-muted-foreground">Memory Usage</p>
                                <p className="font-medium">{iteration.execution_result.memory} KB</p>
                              </div>
                            </CardContent>
                          </Card>
                          <Card>
                            <CardContent className="p-4">
                              <p className="text-sm text-muted-foreground">Output</p>
                              <p className="font-mono">{iteration.execution_result.output}</p>
                            </CardContent>
                          </Card>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Test Results</h4>
                        <div className="rounded-md border">
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Input</TableHead>
                                <TableHead>Expected Output</TableHead>
                                <TableHead>Actual Output</TableHead>
                                <TableHead>Status</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {iteration.test_results.map((test, index) => (
                                <TableRow key={index}>
                                  <TableCell className="font-mono whitespace-pre-wrap">{test.input}</TableCell>
                                  <TableCell className="font-mono whitespace-pre-wrap">{test.expected_output}</TableCell>
                                  <TableCell className="font-mono whitespace-pre-wrap">{test.actual_output}</TableCell>
                                  <TableCell>
                                    {test.passed ? (
                                      <Badge
                                        variant="secondary"
                                        className="bg-green-100 text-green-800 hover:bg-green-100"
                                      >
                                        Passed
                                      </Badge>
                                    ) : (
                                      <Badge variant="destructive">Failed</Badge>
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              ))}
            </Tabs>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

