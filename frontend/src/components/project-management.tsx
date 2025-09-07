import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Loader2, Github, Star, GitFork, RefreshCw, AlertCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface Project {
  name: string
  url: string
  description: string
  three_liner: string
  detailed_paragraph: string
  technologies: string[]
  stars: number
  forks: number
  language: string
  created_at: string
  updated_at: string
}

export function ProjectManagement() {
  const [projects, setProjects] = useState<Project[]>([])
  const [githubUsername, setGithubUsername] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isScraping, setIsScraping] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    setIsLoading(true)
    try {
      const response = await fetch("http://localhost:5000/api/v1/projects")
      if (response.ok) {
        const data = await response.json()
        setProjects(data.projects || [])
      }
    } catch (error) {
      console.error("Failed to load projects:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const scrapeGithub = async () => {
    if (!githubUsername.trim()) {
      toast({
        title: "Error",
        description: "Please enter a GitHub username",
        variant: "destructive",
      })
      return
    }

    setIsScraping(true)
    try {
      const response = await fetch("http://localhost:5000/api/v1/scrape-github", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_username: githubUsername }),
      })

      if (!response.ok) throw new Error("Failed to scrape GitHub")

      const result = await response.json()

      toast({
        title: "Success",
        description: `Scraped ${result.projects_count} projects successfully`,
      })

      // Reload projects after scraping
      await loadProjects()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to scrape GitHub repositories",
        variant: "destructive",
      })
    } finally {
      setIsScraping(false)
    }
  }

  const refreshEmbeddings = async () => {
    setIsRefreshing(true)
    try {
      const response = await fetch("http://localhost:5000/api/v1/refresh-embeddings", {
        method: "POST",
      })

      if (!response.ok) throw new Error("Failed to refresh embeddings")

      toast({
        title: "Success",
        description: "Embeddings refreshed successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to refresh embeddings",
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  const projectsWithoutReadme = projects.filter((p) => !p.description || p.description.trim() === "")

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border p-6">
        <h1 className="font-heading text-2xl font-bold text-foreground">Project Management</h1>
        <p className="text-muted-foreground mt-1">Manage your GitHub repositories and project embeddings</p>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        {/* GitHub Scraping */}
        <Card>
          <CardHeader>
            <CardTitle>GitHub Integration</CardTitle>
            <CardDescription>Scrape repositories from your GitHub profile</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Enter GitHub username"
                value={githubUsername}
                onChange={(e) => setGithubUsername(e.target.value)}
                className="flex-1"
              />
              <Button onClick={scrapeGithub} disabled={isScraping || !githubUsername.trim()}>
                {isScraping ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Scraping...
                  </>
                ) : (
                  <>
                    <Github className="mr-2 h-4 w-4" />
                    Scrape Repos
                  </>
                )}
              </Button>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={refreshEmbeddings} disabled={isRefreshing || projects.length === 0}>
                {isRefreshing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Refreshing...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh Embeddings
                  </>
                )}
              </Button>

              <Button variant="outline" onClick={loadProjects} disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  "Reload Projects"
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Projects without README warning */}
        {projectsWithoutReadme.length > 0 && (
          <Card className="border-destructive/50 bg-destructive/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                Projects Missing README
              </CardTitle>
              <CardDescription>These projects don't have descriptions and may not be properly indexed</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {projectsWithoutReadme.map((project, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                    <span className="font-medium">{project.name}</span>
                    <Badge variant="destructive">No README</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Projects Grid */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-heading text-xl font-semibold">Your Projects ({projects.length})</h2>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : projects.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Github className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="font-medium text-lg mb-2">No Projects Found</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Enter your GitHub username above to scrape your repositories
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((project, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-lg font-medium truncate">{project.name}</CardTitle>
                      <Badge variant="outline" className="ml-2 shrink-0">
                        {project.language || "Unknown"}
                      </Badge>
                    </div>
                    <CardDescription className="line-clamp-2">
                      {project.three_liner || project.description || "No description available"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4" />
                        {project.stars}
                      </div>
                      <div className="flex items-center gap-1">
                        <GitFork className="h-4 w-4" />
                        {project.forks}
                      </div>
                    </div>

                    {project.technologies && project.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {project.technologies.slice(0, 3).map((tech, techIndex) => (
                          <Badge key={techIndex} variant="secondary" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                        {project.technologies.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{project.technologies.length - 3}
                          </Badge>
                        )}
                      </div>
                    )}

                    <Button asChild variant="outline" size="sm" className="w-full bg-transparent">
                      <a href={project.url} target="_blank" rel="noopener noreferrer">
                        <Github className="mr-2 h-4 w-4" />
                        View on GitHub
                      </a>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
