import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { charactersAPI, API_URL } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { Header } from '../components/Header';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '../components/ui/dialog';
import { ArrowLeft, Plus, Trash2, UserCircle, Shield, Heart } from 'lucide-react';
import type { Character } from '../types/character';

function mod(score: number) {
  const m = Math.floor((score - 10) / 2);
  return m >= 0 ? `+${m}` : `${m}`;
}

export default function MyCharacters() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<Character | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const list = await charactersAPI.getAll();
        setCharacters(list);
      } catch (err) {
        console.error('Failed to load characters', err);
        toast({ title: 'Ошибка', description: 'Не удалось загрузить персонажей', variant: 'destructive' });
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await charactersAPI.delete(deleteTarget.id);
      setCharacters(prev => prev.filter(c => c.id !== deleteTarget.id));
      toast({ title: 'Персонаж удалён', description: `"${deleteTarget.name}" удалён` });
    } catch {
      toast({ title: 'Ошибка', description: 'Не удалось удалить персонажа', variant: 'destructive' });
    } finally {
      setIsDeleting(false);
      setDeleteTarget(null);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col relative overflow-hidden"
      style={{
        backgroundImage: 'url(/assets/backgrounds/background2.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div className="relative z-10 flex flex-col flex-1">
        <Header />
        <main className="flex-1 p-6 md:p-10">
          <div className="max-w-6xl mx-auto">
            {/* Top bar */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/')}
                  className="text-foreground hover:bg-white/10"
                >
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Назад
                </Button>
                <h1 className="font-serif text-3xl text-foreground font-bold tracking-wide">
                  Мои персонажи
                </h1>
              </div>
              <Button
                onClick={() => navigate('/characters/create')}
                className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold border-2 border-primary/80"
              >
                <Plus className="w-4 h-4 mr-2" />
                Создать персонажа
              </Button>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-20">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            ) : characters.length === 0 ? (
              <div className="text-center py-24">
                <UserCircle className="w-20 h-20 mx-auto mb-4 text-muted-foreground/50" />
                <p className="text-xl text-muted-foreground mb-2">У вас нет персонажей</p>
                <p className="text-sm text-muted-foreground mb-6">Создайте первого героя для игры</p>
                <Button
                  onClick={() => navigate('/characters/create')}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Создать персонажа
                </Button>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                {characters.map(char => (
                  <Card
                    key={char.id}
                    className="bg-card/90 border-2 border-primary/60 hover:border-primary transition-colors shadow-lg flex flex-col"
                  >
                    {/* Avatar */}
                    <div className="relative w-full aspect-square rounded-t-md overflow-hidden bg-gradient-to-br from-primary/40 to-primary/20 flex items-center justify-center">
                      {char.avatar_url ? (
                        <img
                          src={`${API_URL}${char.avatar_url}`}
                          alt={char.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <UserCircle className="w-20 h-20 text-primary/40" />
                      )}
                      <div className="absolute top-2 right-2">
                        <span className="bg-primary/80 text-primary-foreground text-xs font-bold px-2 py-0.5 rounded">
                          Ур. {char.level}
                        </span>
                      </div>
                    </div>

                    <div className="p-4 flex flex-col flex-1">
                      <h3 className="font-serif text-lg font-bold text-foreground truncate">{char.name}</h3>
                      <p className="text-sm text-primary font-semibold">{char.class}</p>
                      <p className="text-xs text-muted-foreground mb-3">{char.race}</p>

                      {/* Combat stats */}
                      <div className="grid grid-cols-2 gap-2 mb-4">
                        <div className="bg-muted/60 rounded p-2 text-center">
                          <Heart className="w-3 h-3 mx-auto mb-0.5 text-red-400" />
                          <div className="text-xs text-muted-foreground">HP</div>
                          <div className="text-base font-bold text-red-400">{char.current_hp ?? char.max_hp ?? '—'}</div>
                        </div>
                        <div className="bg-muted/60 rounded p-2 text-center">
                          <Shield className="w-3 h-3 mx-auto mb-0.5 text-blue-400" />
                          <div className="text-xs text-muted-foreground">КБ</div>
                          <div className="text-base font-bold text-blue-400">{char.armor_class ?? '—'}</div>
                        </div>
                      </div>

                      {/* Ability scores compact */}
                      <div className="grid grid-cols-6 gap-1 mb-4">
                        {(['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const).map(stat => {
                          const labels: Record<string, string> = {
                            strength: 'СИЛ', dexterity: 'ЛОВ', constitution: 'ТЕЛ',
                            intelligence: 'ИНТ', wisdom: 'МДР', charisma: 'ХАР',
                          };
                          return (
                            <div key={stat} className="text-center">
                              <div className="text-[9px] text-muted-foreground font-bold">{labels[stat]}</div>
                              <div className="text-xs font-bold text-foreground">{char[stat]}</div>
                              <div className="text-[10px] text-accent">{mod(char[stat])}</div>
                            </div>
                          );
                        })}
                      </div>

                      <div className="mt-auto">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteTarget(char)}
                          className="w-full text-destructive hover:bg-destructive/10 hover:text-destructive border border-destructive/30"
                        >
                          <Trash2 className="w-3 h-3 mr-1" />
                          Удалить
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Delete confirmation dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={open => !open && setDeleteTarget(null)}>
        <DialogContent className="bg-card border-2 border-border">
          <DialogHeader>
            <DialogTitle>Удалить персонажа?</DialogTitle>
            <DialogDescription>
              Персонаж <strong>"{deleteTarget?.name}"</strong> будет удалён безвозвратно.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-3 mt-4">
            <Button variant="outline" className="flex-1" onClick={() => setDeleteTarget(null)}>
              Отмена
            </Button>
            <Button
              variant="destructive"
              className="flex-1"
              disabled={isDeleting}
              onClick={handleDelete}
            >
              {isDeleting ? 'Удаление...' : 'Удалить'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
