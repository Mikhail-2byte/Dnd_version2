import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { AlertCircle, Swords } from 'lucide-react';

export default function Auth() {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  
  // Login state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  
  // Register state
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerError, setRegisterError] = useState('');
  
  const { login, register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');

    try {
      await login(loginEmail, loginPassword);
      navigate('/');
    } catch (err: any) {
      setLoginError(err.response?.data?.detail || 'Ошибка входа');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterError('');

    try {
      await register(registerEmail, registerUsername, registerPassword);
      navigate('/');
    } catch (err: any) {
      setRegisterError(err.response?.data?.detail || 'Ошибка регистрации');
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
      style={{
        backgroundImage: 'url(/assets/backgrounds/background2.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Overlay для затемнения фона и улучшения читаемости */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
      
      <div className="relative z-10 text-center px-4 max-w-md w-full mx-auto">
        {/* Переключатель вкладок вверху */}
        <div className="mb-8 flex justify-center">
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'login' | 'register')}>
            <TabsList className="grid w-full grid-cols-2 max-w-xs">
              <TabsTrigger value="login">Вход</TabsTrigger>
              <TabsTrigger value="register">Регистрация</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {activeTab === 'login' ? (
          <>
            {/* Заголовок в стиле Welcome */}
            <div className="mb-8">
              <div className="flex items-center justify-center gap-3 mb-6">
                <div className="w-16 h-16 rounded-lg wood-frame flex items-center justify-center bg-accent/20">
                  <Swords className="w-10 h-10 text-accent" />
                </div>
                <h1 className="text-5xl md:text-6xl font-bold text-foreground tracking-tight">
                  D&D <span className="text-accent gold-glow">Tavern</span>
                </h1>
              </div>
              <p className="text-xl md:text-2xl text-muted-foreground mb-2">
                Добро пожаловать обратно!
              </p>
              <p className="text-lg text-muted-foreground/80">
                Войдите в свой аккаунт, чтобы продолжить приключение
              </p>
            </div>

            {/* Форма входа */}
            <div className="w-full max-w-md mx-auto">
              {loginError && (
                <Alert variant="destructive" className="mb-6">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Ошибка</AlertTitle>
                  <AlertDescription>{loginError}</AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label htmlFor="login-email" className="text-base mb-2 block">Email</Label>
                  <Input
                    type="email"
                    id="login-email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                    placeholder="your@email.com"
                    className="h-11 text-base bg-card/95 backdrop-blur-sm border-2 border-primary/30"
                  />
                </div>

                <div>
                  <Label htmlFor="login-password" className="text-base mb-2 block">Пароль</Label>
                  <Input
                    type="password"
                    id="login-password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                    placeholder="••••••••"
                    className="h-11 text-base bg-card/95 backdrop-blur-sm border-2 border-primary/30"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  size="lg"
                  className="w-full text-lg px-8 py-6 bg-accent hover:bg-accent/90 text-accent-foreground font-semibold shadow-lg hover:shadow-xl transition-all mt-6"
                >
                  {isLoading ? 'Вход...' : 'Войти'}
                </Button>
              </form>
            </div>
          </>
        ) : (
          <>
            {/* Заголовок в стиле Welcome */}
            <div className="mb-8">
              <div className="flex items-center justify-center gap-3 mb-6">
                <div className="w-16 h-16 rounded-lg wood-frame flex items-center justify-center bg-accent/20">
                  <Swords className="w-10 h-10 text-accent" />
                </div>
                <h1 className="text-5xl md:text-6xl font-bold text-foreground tracking-tight">
                  D&D <span className="text-accent gold-glow">Tavern</span>
                </h1>
              </div>
              <p className="text-xl md:text-2xl text-muted-foreground mb-2">
                Создайте свой аккаунт
              </p>
              <p className="text-lg text-muted-foreground/80">
                Присоединяйтесь к миру приключений
              </p>
            </div>

            {/* Форма регистрации */}
            <div className="w-full max-w-md mx-auto">
              {registerError && (
                <Alert variant="destructive" className="mb-6">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Ошибка</AlertTitle>
                  <AlertDescription>{registerError}</AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <Label htmlFor="register-email" className="text-base mb-2 block">Email</Label>
                  <Input
                    type="email"
                    id="register-email"
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    required
                    placeholder="your@email.com"
                    className="h-11 text-base bg-card/95 backdrop-blur-sm border-2 border-primary/30"
                  />
                </div>

                <div>
                  <Label htmlFor="register-username" className="text-base mb-2 block">Имя пользователя</Label>
                  <Input
                    type="text"
                    id="register-username"
                    value={registerUsername}
                    onChange={(e) => setRegisterUsername(e.target.value)}
                    required
                    placeholder="username"
                    className="h-11 text-base bg-card/95 backdrop-blur-sm border-2 border-primary/30"
                  />
                </div>

                <div>
                  <Label htmlFor="register-password" className="text-base mb-2 block">Пароль</Label>
                  <Input
                    type="password"
                    id="register-password"
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    required
                    placeholder="••••••••"
                    className="h-11 text-base bg-card/95 backdrop-blur-sm border-2 border-primary/30"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  size="lg"
                  className="w-full text-lg px-8 py-6 bg-accent hover:bg-accent/90 text-accent-foreground font-semibold shadow-lg hover:shadow-xl transition-all mt-6"
                >
                  {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
                </Button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

