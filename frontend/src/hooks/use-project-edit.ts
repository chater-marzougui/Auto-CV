import { useState } from 'react';
import { config } from '@/config';
import { toast } from 'sonner';
import type { Project } from '@/types/project';
interface EditState {
  three_liner: string;
  technologies: string[];
  suggested_name: string;
}

export const useProjectEdit = () => {
  const [editingProject, setEditingProject] = useState<string | null>(null);
  const [editState, setEditState] = useState<EditState>({ 
    three_liner: '', 
    technologies: [], 
    suggested_name: '' 
  });
  const [isUpdating, setIsUpdating] = useState(false);

  const startEdit = (project: Project) => {
    setEditingProject(project.name);
    setEditState({
      three_liner: project.three_liner || '',
      technologies: project.technologies ? [...project.technologies] : [],
      suggested_name: project.suggested_name || ''
    });
  };

  const cancelEdit = () => {
    setEditingProject(null);
    setEditState({ three_liner: '', technologies: [], suggested_name: '' });
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
      // Update title first (if changed)
      const titleResponse = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.updateProjectTitle.replace('{projectName}', projectName)}`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            suggested_name: editState.suggested_name || null 
          }),
        }
      );

      if (!titleResponse.ok) {
        const errorData = await titleResponse.json();
        throw new Error(errorData.detail || 'Failed to update project title');
      }

      // Update content (three_liner and technologies)
      const contentResponse = await fetch(
        `${config.api.baseUrl}${config.api.endpoints.updateProjectContent.replace('{projectName}', projectName)}`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            three_liner: editState.three_liner,
            technologies: editState.technologies
          }),
        }
      );

      if (!contentResponse.ok) {
        const errorData = await contentResponse.json();
        throw new Error(errorData.detail || 'Failed to update project content');
      }

      toast.success('Project updated successfully', {
        description: 'Content and embeddings have been refreshed',
      });

      setEditingProject(null);
      setEditState({ three_liner: '', technologies: [], suggested_name: '' });
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