import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Separator } from '../components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../hooks/use-toast';
import { 
  Palette, 
  Bell, 
  Volume2, 
  Gamepad2,
  Save,
  RotateCcw
} from 'lucide-react';

interface Settings {
  theme: 'light' | 'dark';
  notifications: boolean;
  soundEffects: boolean;
  musicVolume: number;
  diceAnimations: boolean;
  autoSaveCharacter: boolean;
  combatGridSize: string;
}

const DEFAULT_SETTINGS: Settings = {
  theme: 'dark',
  notifications: true,
  soundEffects: true,
  musicVolume: 50,
  diceAnimations: true,
  autoSaveCharacter: true,
  combatGridSize: 'medium',
};

export default function Settings() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = () => {
    const savedSettings = localStorage.getItem('gameSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...DEFAULT_SETTINGS, ...parsed });
      } catch (error) {
        console.error('Ошибка загрузки настроек:', error);
      }
    }
  };

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);

    // Применяем тему сразу
    if (key === 'theme') {
      applyTheme(value as 'light' | 'dark');
    }
  };

  const applyTheme = (theme: 'light' | 'dark') => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
  };

  const handleSave = () => {
    try {
      localStorage.setItem('gameSettings', JSON.stringify(settings));
      setHasChanges(false);
      toast({
        title: 'Настройки сохранены',
        description: 'Ваши настройки успешно сохранены',
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось сохранить настройки',
        variant: 'destructive',
      });
    }
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
    setHasChanges(true);
    applyTheme(DEFAULT_SETTINGS.theme);
    toast({
      title: 'Настройки сброшены',
      description: 'Настройки возвращены к значениям по умолчанию',
    });
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
      {/* Overlay для затемнения фона */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
      
      <div className="relative z-10 flex flex-col flex-1">
        <Header />
        
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-foreground mb-2">Настройки</h1>
              <p className="text-muted-foreground">
                Настройте параметры игры под свои предпочтения
              </p>
            </div>

            {/* Внешний вид */}
            <Card className="bg-card/95 backdrop-blur-sm border-2 border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="w-5 h-5 text-accent" />
                  Внешний вид
                </CardTitle>
                <CardDescription>
                  Настройки темы и визуального оформления
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="theme">Тема интерфейса</Label>
                    <p className="text-sm text-muted-foreground">
                      Выберите светлую или тёмную тему
                    </p>
                  </div>
                  <Select
                    value={settings.theme}
                    onValueChange={(value: 'light' | 'dark') => updateSetting('theme', value)}
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Светлая</SelectItem>
                      <SelectItem value="dark">Тёмная</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="dice-animations">Анимация кубиков</Label>
                    <p className="text-sm text-muted-foreground">
                      Включить анимацию при броске кубиков
                    </p>
                  </div>
                  <Switch
                    id="dice-animations"
                    checked={settings.diceAnimations}
                    onCheckedChange={(checked) => updateSetting('diceAnimations', checked)}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Уведомления */}
            <Card className="bg-card/95 backdrop-blur-sm border-2 border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="w-5 h-5 text-accent" />
                  Уведомления
                </CardTitle>
                <CardDescription>
                  Управление уведомлениями в игре
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="notifications">Уведомления</Label>
                    <p className="text-sm text-muted-foreground">
                      Показывать уведомления о событиях в игре
                    </p>
                  </div>
                  <Switch
                    id="notifications"
                    checked={settings.notifications}
                    onCheckedChange={(checked) => updateSetting('notifications', checked)}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Звук и музыка */}
            <Card className="bg-card/95 backdrop-blur-sm border-2 border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Volume2 className="w-5 h-5 text-accent" />
                  Звук и музыка
                </CardTitle>
                <CardDescription>
                  Настройки звуковых эффектов и музыки
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="sound-effects">Звуковые эффекты</Label>
                    <p className="text-sm text-muted-foreground">
                      Воспроизводить звуки при действиях
                    </p>
                  </div>
                  <Switch
                    id="sound-effects"
                    checked={settings.soundEffects}
                    onCheckedChange={(checked) => updateSetting('soundEffects', checked)}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Игровой процесс */}
            <Card className="bg-card/95 backdrop-blur-sm border-2 border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gamepad2 className="w-5 h-5 text-accent" />
                  Игровой процесс
                </CardTitle>
                <CardDescription>
                  Настройки механики игры
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="auto-save">Автосохранение персонажа</Label>
                    <p className="text-sm text-muted-foreground">
                      Автоматически сохранять изменения персонажа
                    </p>
                  </div>
                  <Switch
                    id="auto-save"
                    checked={settings.autoSaveCharacter}
                    onCheckedChange={(checked) => updateSetting('autoSaveCharacter', checked)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="grid-size">Размер сетки боя</Label>
                    <p className="text-sm text-muted-foreground">
                      Размер ячеек на боевой карте
                    </p>
                  </div>
                  <Select
                    value={settings.combatGridSize}
                    onValueChange={(value) => updateSetting('combatGridSize', value)}
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="small">Маленький</SelectItem>
                      <SelectItem value="medium">Средний</SelectItem>
                      <SelectItem value="large">Большой</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Кнопки действий */}
            <div className="flex gap-4 justify-end sticky bottom-0 bg-background/80 backdrop-blur-sm p-4 rounded-lg border border-border">
              <Button
                variant="outline"
                onClick={handleReset}
                className="gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Сбросить
              </Button>
              <Button
                onClick={handleSave}
                disabled={!hasChanges}
                className="gap-2"
              >
                <Save className="w-4 h-4" />
                Сохранить изменения
              </Button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

