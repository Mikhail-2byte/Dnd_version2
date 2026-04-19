import { Swords, Home, User, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"

export function Header() {
  const navigate = useNavigate()

  return (
    <header className="border-b-4 border-primary/30 bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-[1800px] mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-lg wood-frame flex items-center justify-center">
            <Swords className="w-7 h-7 text-accent" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">
              D&D <span className="text-accent gold-glow">Tavern</span>
            </h1>
            <p className="text-xs text-muted-foreground">Adventure Awaits</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex gap-2 items-center">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="gap-2"
          >
            <Home className="w-4 h-4" />
            Главное меню
          </Button>
          <Button
            variant="ghost"
            onClick={() => navigate("/profile")}
            className="gap-2"
          >
            <User className="w-4 h-4" />
            Профиль
          </Button>
          <Button
            variant="ghost"
            onClick={() => navigate("/settings")}
            className="gap-2"
          >
            <Settings className="w-4 h-4" />
            Настройки
          </Button>
        </nav>
      </div>
    </header>
  )
}

