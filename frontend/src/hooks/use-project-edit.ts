import { useState } from 'react';
import { config } from '@/config';
import { toast } from 'sonner';

interface Project {
  name: string;
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

interface EditState {
  three_liner: string;
  technologies: string[];
}

export const useProjectEdit = () => {
  const [editingProject, setEditingProject] = useState<string | null>(null);
  const [editState, setEditState] = useState<EditState>({ three_liner: '', technologies: [] });
  const [isUpdating, setIsUpdating] = useState(false);

  const startEdit = (project: Project) => {
    setEditingProject(project.name);
    setEditState({
      three_liner: project.three_liner || '',
      technologies: project.technologies ? [...project.technologies] : []
    });
  };

  const cancelEdit = () => {
    setEditingProject(null);
    setEditState({ three_liner: '', technologies: [] });
  };

  const updateEditState = (field: keyof EditState, value: string | string[]) => {
    setEditState(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveEdit = async (projectName: string): Promise<boolean> => {
    if (!editingProject || editingProject !== projectName) return false;

    setIsUpdating(true);
    try {
      const response = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.updateProjectContent.replace('{projectName}', projectName)}`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(editState),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update project content');
      }

      toast.success('Project updated successfully', {
        description: 'Content and embeddings have been refreshed',
      });

      setEditingProject(null);
      setEditState({ three_liner: '', technologies: [] });
      return true;
    } catch (error) {
      toast.error('Failed to update project', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
      });
      return false;
    } finally {
      setIsUpdating(false);
    }
  };

  return {
    editingProject,
    editState,
    isUpdating,
    startEdit,
    cancelEdit,
    updateEditState,
    saveEdit,
  };
};