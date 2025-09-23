
export interface Project {
  name: string;
  suggested_name?: string;
  url: string;
  description: string;
  three_liner: string;
  detailed_paragraph: string;
  technologies: string[];
  bad_readme: boolean;
  no_readme: boolean;
  stars: number;
  forks: number;
  language: string;
  created_at: string;
  updated_at: string;
  hidden_from_search?: boolean;
}

export interface MatchedProject {
  project: Project;
  similarity_score: number;
}