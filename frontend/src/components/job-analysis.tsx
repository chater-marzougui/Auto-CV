"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Loader2, Send, FileText, Mail } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { config } from "@/config"

interface JobAnalysisResult {
  required_technologies: string[]
  experience_level: string
  analysis_summary: string
  matched_projects: Array<{
    name: string
    similarity_score: number
  }>
  cv_download_url?: string
  cover_letter_download_url?: string
}

export function JobAnalysis() {
  const [jobDescription, setJobDescription] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<JobAnalysisResult | null>(null)
  const { toast } = useToast()

  const analyzeJob = async () => {
    if (!jobDescription.trim()) {
      toast({
        title: "Error",
        description: "Please enter a job description",
        variant: "destructive",
      })
      return
    }

    setIsAnalyzing(true)
    try {
      const response = await fetch(`${config.api.baseUrl}${config.api.endpoints.analyzeJob}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "Job Position",
          company: "Company",
          description: jobDescription,
        }),
      })

      if (!response.ok) throw new Error("Failed to analyze job")

      const analysis = await response.json()

      // Also get matching projects
      const matchResponse = await fetch(`${config.api.baseUrl}${config.api.endpoints.matchProjects}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: jobDescription }),
      })

      let matchedProjects = []
      if (matchResponse.ok) {
        matchedProjects = await matchResponse.json()
      }

      setAnalysisResult({
        ...analysis,
        matched_projects: matchedProjects.map((mp: any) => ({
          name: mp.project.name,
          similarity_score: mp.similarity_score,
        })),
      })

      toast({
        title: "Analysis Complete",
        description: "Job description analyzed successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to analyze job description" + (error instanceof Error ? `: ${error.message}` : ""),
        variant: "destructive",
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const generateApplication = async () => {
    setIsGenerating(true)
    try {
      const response = await fetch(`${config.api.baseUrl}${config.api.endpoints.generateApplication}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_description: jobDescription,
          personal_info: {
            first_name: "John",
            last_name: "Doe",
            email: "john.doe@example.com",
            phone: "+1-555-0123",
            address: "123 Tech Street",
            city: "San Francisco",
            postal_code: "94105",
            title: "Software Developer",
            summary: "Experienced software developer with expertise in modern web technologies.",
            skills: {
              "Programming Languages": ["Python", "JavaScript", "TypeScript"],
              "Web Frameworks": ["React", "FastAPI", "Next.js"],
              Databases: ["PostgreSQL", "MongoDB"],
              Tools: ["Docker", "Git", "AWS"],
            },
            experience: [],
            education: [],
          },
          top_k: 4,
        }),
      })

      if (!response.ok) throw new Error("Failed to generate application")

      const result = await response.json()

      setAnalysisResult((prev) =>
        prev
          ? {
              ...prev,
              cv_download_url: result.cv.download_url,
              cover_letter_download_url: result.cover_letter.download_url,
            }
          : null,
      )

      toast({
        title: "Application Generated",
        description: "CV and cover letter generated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate application" + (error instanceof Error ? `: ${error.message}` : ""),
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border p-6">
        <h1 className="font-heading text-2xl font-bold text-foreground">Job Analysis</h1>
        <p className="text-muted-foreground mt-1">
          Paste a job description to analyze requirements and generate tailored applications
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle>Job Description</CardTitle>
            <CardDescription>Paste the job description you want to apply for</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="min-h-[200px]"
            />
            <div className="flex gap-2">
              <Button onClick={analyzeJob} disabled={isAnalyzing || !jobDescription.trim()} className="flex-1">
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Analyze Job
                  </>
                )}
              </Button>
              {analysisResult && (
                <Button onClick={generateApplication} disabled={isGenerating} variant="secondary">
                  {isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-4 w-4" />
                      Generate Application
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {analysisResult && (
          <div className="space-y-4">
            {/* Job Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Analysis Results</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Required Technologies</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.required_technologies.map((tech, index) => (
                      <Badge key={index} variant="secondary">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Experience Level</h4>
                  <Badge variant="outline">{analysisResult.experience_level}</Badge>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Summary</h4>
                  <p className="text-sm text-muted-foreground">{analysisResult.analysis_summary}</p>
                </div>
              </CardContent>
            </Card>

            {/* Matched Projects */}
            <Card>
              <CardHeader>
                <CardTitle>Matched Projects</CardTitle>
                <CardDescription>Projects from your GitHub that best match this job</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysisResult.matched_projects.map((project, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                      <span className="font-medium">{project.name}</span>
                      <Badge variant="secondary">{(project.similarity_score * 100).toFixed(1)}% match</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Download Section */}
            {(analysisResult.cv_download_url || analysisResult.cover_letter_download_url) && (
              <Card>
                <CardHeader>
                  <CardTitle>Generated Documents</CardTitle>
                  <CardDescription>Download your tailored CV and cover letter</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4">
                    {analysisResult.cv_download_url && (
                      <Button asChild>
                        <a
                          href={`${config.api.baseUrl}${analysisResult.cv_download_url}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          <FileText className="mr-2 h-4 w-4" />
                          Download CV
                        </a>
                      </Button>
                    )}
                    {analysisResult.cover_letter_download_url && (
                      <Button asChild variant="secondary">
                        <a
                          href={`${config.api.baseUrl}${analysisResult.cover_letter_download_url}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          <Mail className="mr-2 h-4 w-4" />
                          Download Cover Letter
                        </a>
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
