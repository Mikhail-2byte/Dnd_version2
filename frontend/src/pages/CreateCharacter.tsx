import { useNavigate } from 'react-router-dom';
import CharacterCreation from '../components/CharacterCreation';
import { charactersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import type { CharacterCreate } from '../types/character';

export default function CreateCharacter() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (data: CharacterCreate) => {
    try {
      await charactersAPI.create(data);
      toast({
        title: 'Персонаж создан!',
        description: `Персонаж "${data.name}" успешно создан`,
      });
      navigate('/characters');
    } catch (error: any) {
      console.error('Error creating character:', error);
      const errorMessage = error.response?.data?.detail || 'Ошибка создания персонажа';
      toast({
        title: 'Ошибка',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  return (
    <CharacterCreation
      onSubmit={handleSubmit}
      onCancel={() => navigate('/characters')}
    />
  );
}

