"use client"

import { Swords, Map, Users, UserPlus } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface HeaderProps {
  activeTab: "lobby" | "maps" | "characters"
  onTabChange: (tab: "lobby" | "maps" | "characters") => void
}

export function Header({ activeTab, onTabChange }: HeaderProps) {
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
        <nav className="flex gap-2">
          <Button
            variant={activeTab === "lobby" ? "default" : "ghost"}
            onClick={() => onTabChange("lobby")}
            className="gap-2"
          >
            <Users className="w-4 h-4" />
            Лобби
          </Button>
          <Button
            variant={activeTab === "maps" ? "default" : "ghost"}
            onClick={() => onTabChange("maps")}
            className="gap-2"
          >
            <Map className="w-4 h-4" />
            Карты
          </Button>
          <Button
            variant={activeTab === "characters" ? "default" : "ghost"}
            onClick={() => onTabChange("characters")}
            className="gap-2"
          >
            <Swords className="w-4 h-4" />
            Персонажи
          </Button>
          <Link href="/create-character">
            <Button variant="outline" className="gap-2 border-accent/50 hover:border-accent bg-transparent">
              <UserPlus className="w-4 h-4" />
              Создать героя
            </Button>
          </Link>
        </nav>
      </div>
    </header>
  )
}
