
export interface Experience {
  company: string;
  position: string;
  start_date: string;
  end_date: string;
  description: string;
}

export interface Education {
  institution: string;
  degree: string;
  field: string;
  start_date: string;
  end_date: string;
  description: string;
}

export interface PersonalInfo {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  title?: string;
  summary?: string;
  skills?: { [category: string]: string[] };
  experience?: Experience[];
  education?: Education[];
}