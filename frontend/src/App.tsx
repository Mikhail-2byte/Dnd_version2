import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ThemeProvider } from './components/ThemeProvider';
import { Toaster } from './components/ui/toaster';
import Welcome from './pages/Welcome';
import Auth from './pages/Auth';
import MainMenu from './pages/MainMenu';
import GameRoom from './pages/GameRoom';
import GameLobby from './pages/GameLobby';
import CreateGameSelection from './pages/CreateGameSelection';
import CreateGameNew from './pages/CreateGameNew';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import MyCharacters from './pages/MyCharacters';
import CreateCharacter from './pages/CreateCharacter';
import MyScenarios from './pages/MyScenarios';
import ScenarioBuilder from './pages/ScenarioBuilder';

// Компонент для обработки глобальных событий авторизации
function AuthEventHandler() {
  const { logout } = useAuthStore();

  useEffect(() => {
    const handleAuthLogout = () => {
      logout();
    };

    window.addEventListener('auth:logout', handleAuthLogout);
    return () => {
      window.removeEventListener('auth:logout', handleAuthLogout);
    };
  }, [logout]);

  return null;
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading, hasCheckedAuth, checkAuth } = useAuthStore();

  useEffect(() => {
    if (!hasCheckedAuth) {
      checkAuth();
    }
  }, [checkAuth, hasCheckedAuth]);

  // Показываем загрузку пока проверяется авторизация
  if (isLoading || !hasCheckedAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Загрузка...</p>
        </div>
      </div>
    );
  }

  // Редиректим на welcome только после завершения проверки
  if (!user) {
    return <Navigate to="/welcome" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AuthEventHandler />
        <Routes>
          <Route path="/welcome" element={<Welcome />} />
          <Route path="/auth" element={<Auth />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainMenu />
              </ProtectedRoute>
            }
          />
          <Route
            path="/game/:gameId/lobby"
            element={
              <ProtectedRoute>
                <GameLobby />
              </ProtectedRoute>
            }
          />
          <Route
            path="/game/:gameId"
            element={
              <ProtectedRoute>
                <GameRoom />
              </ProtectedRoute>
            }
          />
          <Route
            path="/create-game"
            element={
              <ProtectedRoute>
                <CreateGameSelection />
              </ProtectedRoute>
            }
          />
          <Route
            path="/create-game/new"
            element={
              <ProtectedRoute>
                <CreateGameNew />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/characters"
            element={
              <ProtectedRoute>
                <MyCharacters />
              </ProtectedRoute>
            }
          />
          <Route
            path="/characters/create"
            element={
              <ProtectedRoute>
                <CreateCharacter />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scenarios"
            element={
              <ProtectedRoute>
                <MyScenarios />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scenarios/builder"
            element={
              <ProtectedRoute>
                <ScenarioBuilder />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scenarios/builder/:scenarioId"
            element={
              <ProtectedRoute>
                <ScenarioBuilder />
              </ProtectedRoute>
            }
          />
        </Routes>
        <Toaster />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;

