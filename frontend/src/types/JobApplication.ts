export interface JobApplication {
  id: number;
  personal_info_id: number;
  job_title: string;
  company_name: string;
  job_description?: string;
  job_requirements?: string;
  cv_file_path?: string;
  cover_letter_file_path?: string;
  cv_download_url?: string;
  cover_letter_download_url?: string;
  matched_projects?: Record<string, unknown>[];
  application_date: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface JobApplicationCreate {
  personal_info_id: number;
  job_title: string;
  company_name: string;
  job_description?: string;
  job_requirements?: string;
  status?: string;
  notes?: string;
}

export interface JobApplicationUpdate {
  job_title?: string;
  company_name?: string;
  job_description?: string;
  job_requirements?: string;
  status?: string;
  notes?: string;
}