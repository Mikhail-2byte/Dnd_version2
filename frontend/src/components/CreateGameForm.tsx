import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import { AlertCircle, Upload, X } from 'lucide-react';

interface CreateGameFormProps {
  onSubmit: (data: { name: string; story?: string; mapFile?: File }) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export default function CreateGameForm({ onSubmit, onCancel, isLoading }: CreateGameFormProps) {
  const [name, setName] = useState('');
  const [story, setStory] = useState('');
  const [mapFile, setMapFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Файл должен быть изображением');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError('Размер файла не должен превышать 10 МБ');
        return;
      }
      setMapFile(file);
      setError('');
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveFile = () => {
    setMapFile(null);
    setPreview(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Введите название игры');
      return;
    }

    try {
      await onSubmit({
        name: name.trim(),
        story: story.trim() || undefined,
        mapFile: mapFile || undefined,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка создания игры');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="game-name">Название игры *</Label>
        <Input
          id="game-name"
          type="text"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setError('');
          }}
          required
          placeholder="Например: Приключение в подземельях"
          disabled={isLoading}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="game-story">Сюжет игры (опционально)</Label>
        <Textarea
          id="game-story"
          value={story}
          onChange={(e) => {
            setStory(e.target.value);
            setError('');
          }}
          placeholder="Опишите сюжет вашей игры, предысторию, цели героев..."
          rows={8}
          disabled={isLoading}
          className="resize-none"
        />
        <p className="text-sm text-muted-foreground">
          Опишите сюжет, предысторию и цели для героев (необязательно)
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="game-map">Карта игры (опционально)</Label>
        <div className="space-y-4">
          {preview ? (
            <div className="relative">
              <img
                src={preview}
                alt="Предпросмотр карты"
                className="w-full h-48 object-cover rounded-md border"
              />
              <Button
                type="button"
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2"
                onClick={handleRemoveFile}
                disabled={isLoading}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          ) : (
            <div className="border-2 border-dashed border-border rounded-md p-6 text-center">
              <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
              <Label
                htmlFor="game-map"
                className="cursor-pointer text-sm text-muted-foreground hover:text-foreground"
              >
                Нажмите для загрузки карты
              </Label>
              <Input
                id="game-map"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                disabled={isLoading}
              />
            </div>
          )}
        </div>
        <p className="text-sm text-muted-foreground">
          Загрузите изображение карты для игры (JPG, PNG, до 10 МБ)
        </p>
      </div>

      <div className="flex gap-3 pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1"
        >
          Отмена
        </Button>
        <Button
          type="submit"
          disabled={isLoading || !name.trim()}
          className="flex-1"
        >
          {isLoading ? 'Создание...' : 'Создать игру'}
        </Button>
      </div>
    </form>
  );
}

