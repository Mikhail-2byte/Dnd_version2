import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Play, Pencil, Trash2, ArrowLeft, BookOpen, Users, Package } from 'lucide-react';
import { Header } from '../components/Header';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel,
  AlertDialogContent, AlertDialogDescription, AlertDialogFooter,
  AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { useToast } from '../hooks/use-toast';
import { scenariosAPI } from '../services/api';
import type { ScenarioListItem } from '../types/scenario';

export default function MyScenarios() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState<string | null>(null);

  useEffect(() => {
    scenariosAPI.list().then(setScenarios).finally(() => setLoading(false));
  }, []);

  const handleLaunch = async (id: string) => {
    setLaunching(id);
    try {
      const game = await scenariosAPI.launch(id);
      toast({ title: 'Игра создана!', description: 'Переходим в лобби...' });
      navigate(`/game/${game.id}/lobby`);
    } catch {
      toast({ title: 'Ошибка', description: 'Не удалось запустить сценарий', variant: 'destructive' });
    } finally {
      setLaunching(null);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await scenariosAPI.delete(id);
      setScenarios((prev) => prev.filter((s) => s.id !== id));
      toast({ title: 'Сценарий удалён' });
    } catch {
      toast({ title: 'Ошибка', description: 'Не удалось удалить сценарий', variant: 'destructive' });
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col relative overflow-hidden"
      style={{
        backgroundImage: 'url(/assets/backgrounds/background2.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative z-10 flex flex-col flex-1">
        <Header />
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-5xl mx-auto">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => navigate('/create-game')}
                  className="hover:bg-accent/10">
                  <ArrowLeft className="w-5 h-5" />
                </Button>
                <div>
                  <h1 className="text-3xl font-bold text-foreground mb-1">Мои сценарии</h1>
                  <p className="text-muted-foreground">Сохранённые приключения для запуска</p>
                </div>
              </div>
              <Button onClick={() => navigate('/scenarios/builder')} className="gap-2" size="lg">
                <Plus className="w-5 h-5" />
                Новый сценарий
              </Button>
            </div>

            {loading && (
              <div className="flex items-center justify-center py-20">
                <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            )}

            {!loading && scenarios.length === 0 && (
              <div className="text-center py-20 text-muted-foreground">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg">У вас пока нет сценариев</p>
                <p className="text-sm mt-1">Создайте первый сценарий и подготовьте своё приключение</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {scenarios.map((s) => (
                <Card key={s.id} className="bg-card/80 backdrop-blur-sm border-border/50">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-start justify-between gap-2">
                      <span className="truncate">{s.name}</span>
                      <span className="text-xs font-normal text-muted-foreground shrink-0">
                        {new Date(s.created_at).toLocaleDateString('ru-RU')}
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {s.story && (
                      <p className="text-sm text-muted-foreground line-clamp-2">{s.story}</p>
                    )}
                    <div className="flex gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" /> {s.npc_count} НПС
                      </span>
                      <span className="flex items-center gap-1">
                        <Package className="w-3 h-3" /> {s.item_count} предметов
                      </span>
                      {s.map_url && <span className="text-green-400">Карта загружена</span>}
                    </div>
                    <div className="flex gap-2 pt-1">
                      <Button size="sm" className="gap-1 flex-1" disabled={launching === s.id}
                        onClick={() => handleLaunch(s.id)}>
                        {launching === s.id
                          ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          : <Play className="w-3 h-3" />}
                        Запустить
                      </Button>
                      <Button size="sm" variant="outline" className="gap-1"
                        onClick={() => navigate(`/scenarios/builder/${s.id}`)}>
                        <Pencil className="w-3 h-3" />
                        Редактировать
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button size="sm" variant="destructive" className="gap-1">
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Удалить сценарий?</AlertDialogTitle>
                            <AlertDialogDescription>
                              Сценарий «{s.name}» будет удалён безвозвратно.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Отмена</AlertDialogCancel>
                            <AlertDialogAction onClick={() => handleDelete(s.id)}>
                              Удалить
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
