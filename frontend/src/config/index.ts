export const config = {
  // Backend API configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000",
    endpoints: {
      projects: "/api/v1/projects",
      scrapeGithub: "/api/v1/scrape-github", 
      refreshEmbeddings: "/api/v1/refresh-embeddings",
      analyzeJob: "/api/v1/analyze-job",
      matchProjects: "/api/v1/match-projects",
      generateApplication: "/api/v1/generate-full-application",
      toggleProjectVisibility: "/api/v1/projects/{projectName}/visibility",
      updateProject: "/api/v1/projects/{projectName}/update",
      updateProjectContent: "/api/v1/projects/{projectName}/content"
    }
  },
  
  // UI configuration
  ui: {
    themes: {
      light: "light",
      dark: "dark",
      system: "system"
    }
  }
} as const

export type Config = typeof config