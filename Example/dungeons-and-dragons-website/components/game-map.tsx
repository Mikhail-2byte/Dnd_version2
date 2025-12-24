"use client"

import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface GameMapProps {
  onCharacterSelect: (id: string) => void
}

const characterTokens = [
  { id: "1", name: "Торин", x: 25, y: 30, avatar: "/dwarf-warrior-portrait.jpg" },
  { id: "2", name: "Эльдара", x: 65, y: 45, avatar: "/elf-mage-portrait.jpg" },
  { id: "3", name: "Гримм", x: 45, y: 60, avatar: "/human-rogue-portrait.jpg" },
  { id: "4", name: "Лира", x: 75, y: 25, avatar: "/halfling-bard-portrait.jpg" },
]

export function GameMap({ onCharacterSelect }: GameMapProps) {
  return (
    <Card className="flex-1 border-2 border-border bg-card/95 backdrop-blur-sm overflow-hidden">
      <div className="relative w-full h-full min-h-[600px]">
        {/* Map Background */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-90"
          style={{
            backgroundImage:
              "url(https://hebbkx1anhila5yf.public.blob.vercel-storage.com/b1b998884b07b9a50be1ec065e3f6689-MtVxFPF59ftwrsUmOT39P5GmHLrHea.jpg)",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />

        {/* Grid Overlay */}
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(to right, oklch(0.30 0.02 40) 1px, transparent 1px),
              linear-gradient(to bottom, oklch(0.30 0.02 40) 1px, transparent 1px)
            `,
            backgroundSize: "40px 40px",
          }}
        />

        {/* Character Tokens */}
        {characterTokens.map((token) => (
          <button
            key={token.id}
            onClick={() => onCharacterSelect(token.id)}
            className="absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
            style={{ left: `${token.x}%`, top: `${token.y}%` }}
          >
            <div className="relative">
              <Avatar className="w-14 h-14 border-4 border-accent shadow-lg ring-4 ring-accent/30 group-hover:ring-accent/60 transition-all group-hover:scale-110">
                <AvatarImage src={token.avatar || "/placeholder.svg"} alt={token.name} />
                <AvatarFallback className="bg-primary text-primary-foreground font-bold">
                  {token.name[0]}
                </AvatarFallback>
              </Avatar>
              <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap bg-card/95 px-2 py-0.5 rounded border border-border text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                {token.name}
              </div>
            </div>
          </button>
        ))}

        {/* Map Info Overlay */}
        <div className="absolute top-4 left-4 bg-card/90 backdrop-blur-sm border-2 border-border rounded-lg p-3 shadow-lg">
          <h3 className="font-bold text-sm text-foreground mb-1">Таверна "Золотой дракон"</h3>
          <p className="text-xs text-muted-foreground">Место сбора искателей приключений</p>
        </div>
      </div>
    </Card>
  )
}
