import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Circle } from "lucide-react"

const players = [
  { id: 1, name: "Торин", status: "online", avatar: "/dwarf-warrior.png" },
  { id: 2, name: "Эльдара", status: "ready", avatar: "/elf-mage.jpg" },
  { id: 3, name: "Гримм", status: "online", avatar: "/human-rogue.jpg" },
  { id: 4, name: "Лира", status: "ready", avatar: "/halfling-bard.jpg" },
  { id: 5, name: "Драгос", status: "offline", avatar: "/dragonborn-paladin.jpg" },
]

export function PlayerSidebar() {
  return (
    <Card className="w-72 p-4 border-2 border-border bg-card/95 backdrop-blur-sm">
      <div className="space-y-4">
        <div className="border-b border-border pb-3">
          <h2 className="text-lg font-bold text-foreground">Игроки в лобби</h2>
          <p className="text-sm text-muted-foreground">4 из 5 готовы</p>
        </div>

        <div className="space-y-2">
          {players.map((player) => (
            <div key={player.id} className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/50 transition-colors">
              <Avatar className="w-10 h-10 border-2 border-border">
                <AvatarImage src={player.avatar || "/placeholder.svg"} alt={player.name} />
                <AvatarFallback>{player.name[0]}</AvatarFallback>
              </Avatar>

              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-foreground truncate">{player.name}</p>
                <div className="flex items-center gap-1.5">
                  <Circle
                    className={`w-2 h-2 fill-current ${
                      player.status === "ready"
                        ? "text-green-600"
                        : player.status === "online"
                          ? "text-yellow-600"
                          : "text-gray-400"
                    }`}
                  />
                  <span className="text-xs text-muted-foreground capitalize">
                    {player.status === "ready" ? "Готов" : player.status === "online" ? "Онлайн" : "Оффлайн"}
                  </span>
                </div>
              </div>

              {player.status === "ready" && (
                <Badge variant="secondary" className="text-xs bg-accent/20 text-accent-foreground border-accent/30">
                  ✓
                </Badge>
              )}
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
