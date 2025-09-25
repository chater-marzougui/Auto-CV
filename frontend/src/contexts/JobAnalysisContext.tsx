import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { MatchedProject } from "@/types/project";

interface JobAnalysisResult {
  job_analysis_result: JobDescriptionResult;
  matched_projects: Array<{
    name: string;
    similarity_score: number;
  }>;
  cv_download_url?: string;
  cover_letter_download_url?: string;
}

interface JobDescriptionResult {
  title: string;
  company: string;
  required_technologies: string[];
  experience_level: string;
  soft_skills: string[];
  analysis_summary: string;
  full_description: string;
  requirements: string;
}

interface JobAnalysisState {
  jobDescription: string;
  analysisResult: JobAnalysisResult | null;
  matchedProjects: MatchedProject[];
  selectedProjects: MatchedProject[];
  isAnalyzing: boolean;
  isGenerating: boolean;
  showProgress: boolean;
}

interface JobAnalysisContextType extends JobAnalysisState {
  setJobDescription: (description: string) => void;
  setAnalysisResult: (result: JobAnalysisResult | null) => void;
  setMatchedProjects: (projects: MatchedProject[]) => void;
  setSelectedProjects: (projects: MatchedProject[]) => void;
  setIsAnalyzing: (analyzing: boolean) => void;
  setIsGenerating: (generating: boolean) => void;
  setShowProgress: (show: boolean) => void;
  clearState: () => void;
}

const initialState: JobAnalysisState = {
  jobDescription: "",
  analysisResult: null,
  matchedProjects: [],
  selectedProjects: [],
  isAnalyzing: false,
  isGenerating: false,
  showProgress: false,
};

const JobAnalysisContext = createContext<JobAnalysisContextType | undefined>(undefined);

const STORAGE_KEY = "auto-cv-job-analysis-state";

export function JobAnalysisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<JobAnalysisState>(initialState);

  // Load state from localStorage on mount
  useEffect(() => {
    try {
      const savedState = localStorage.getItem(STORAGE_KEY);
      if (savedState) {
        const parsedState = JSON.parse(savedState);
        // Only restore persistent data, not loading states
        setState(prevState => ({
          ...prevState,
          jobDescription: parsedState.jobDescription || "",
          analysisResult: parsedState.analysisResult || null,
          matchedProjects: parsedState.matchedProjects || [],
          selectedProjects: parsedState.selectedProjects || [],
        }));
      }
    } catch (error) {
      console.error("Failed to load job analysis state from localStorage:", error);
    }
  }, []);

  // Save state to localStorage whenever it changes (excluding loading states)
  useEffect(() => {
    try {
      const stateToSave = {
        jobDescription: state.jobDescription,
        analysisResult: state.analysisResult,
        matchedProjects: state.matchedProjects,
        selectedProjects: state.selectedProjects,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
    } catch (error) {
      console.error("Failed to save job analysis state to localStorage:", error);
    }
  }, [state.jobDescription, state.analysisResult, state.matchedProjects, state.selectedProjects]);

  const setJobDescription = (description: string) => {
    setState(prev => ({ ...prev, jobDescription: description }));
  };

  const setAnalysisResult = (result: JobAnalysisResult | null) => {
    setState(prev => ({ ...prev, analysisResult: result }));
  };

  const setMatchedProjects = (projects: MatchedProject[]) => {
    setState(prev => ({ ...prev, matchedProjects: projects }));
  };

  const setSelectedProjects = (projects: MatchedProject[]) => {
    setState(prev => ({ ...prev, selectedProjects: projects }));
  };

  const setIsAnalyzing = (analyzing: boolean) => {
    setState(prev => ({ ...prev, isAnalyzing: analyzing }));
  };

  const setIsGenerating = (generating: boolean) => {
    setState(prev => ({ ...prev, isGenerating: generating }));
  };

  const setShowProgress = (show: boolean) => {
    setState(prev => ({ ...prev, showProgress: show }));
  };

  const clearState = () => {
    setState(initialState);
    localStorage.removeItem(STORAGE_KEY);
  };

  const contextValue: JobAnalysisContextType = {
    ...state,
    setJobDescription,
    setAnalysisResult,
    setMatchedProjects,
    setSelectedProjects,
    setIsAnalyzing,
    setIsGenerating,
    setShowProgress,
    clearState,
  };

  return (
    <JobAnalysisContext.Provider value={contextValue}>
      {children}
    </JobAnalysisContext.Provider>
  );
}

export function useJobAnalysis() {
  const context = useContext(JobAnalysisContext);
  if (context === undefined) {
    throw new Error("useJobAnalysis must be used within a JobAnalysisProvider");
  }
  return context;
}