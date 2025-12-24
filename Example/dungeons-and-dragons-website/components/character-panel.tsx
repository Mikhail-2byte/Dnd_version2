import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Sword, Shield, Heart, Zap, Brain, Users } from "lucide-react"

const characters = [
  {
    id: "1",
    name: "Торин Железная Борода",
    class: "Воин",
    level: 5,
    avatar: "/dwarf-warrior-portrait.jpg",
    stats: { str: 18, dex: 12, con: 16, int: 10, wis: 13, cha: 8 },
    hp: 52,
    maxHp: 52,
  },
  {
    id: "2",
    name: "Эльдара Лунный Свет",
    class: "Маг",
    level: 5,
    avatar: "/elf-mage-portrait.jpg",
    stats: { str: 8, dex: 14, con: 12, int: 18, wis: 15, cha: 13 },
    hp: 28,
    maxHp: 28,
  },
  {
    id: "3",
    name: "Гримм Тенехват",
    class: "Плут",
    level: 5,
    avatar: "/human-rogue-portrait.jpg",
    stats: { str: 12, dex: 18, con: 14, int: 13, wis: 12, cha: 14 },
    hp: 38,
    maxHp: 38,
  },
  {
    id: "4",
    name: "Лира Веселая Песня",
    class: "Бард",
    level: 5,
    avatar: "/halfling-bard-portrait.jpg",
    stats: { str: 10, dex: 15, con: 12, int: 13, wis: 11, cha: 18 },
    hp: 32,
    maxHp: 32,
  },
]

interface CharacterPanelProps {
  selectedId: string | null
}

export function CharacterPanel({ selectedId }: CharacterPanelProps) {
  return (
    <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
      {characters.map((character) => (
        <Card
          key={character.id}
          className={`p-6 border-2 transition-all ${
            selectedId === character.id ? "border-accent shadow-lg ring-2 ring-accent/30" : "border-border bg-card/95"
          }`}
        >
          <div className="flex gap-4">
            {/* Character Portrait */}
            <Avatar className="w-24 h-24 border-4 border-border shadow-md">
              <AvatarImage src={character.avatar || "/placeholder.svg"} alt={character.name} />
              <AvatarFallback className="text-2xl font-bold bg-primary text-primary-foreground">
                {character.name[0]}
              </AvatarFallback>
            </Avatar>

            {/* Character Info */}
            <div className="flex-1 space-y-2">
              <div>
                <h3 className="text-lg font-bold text-foreground">{character.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="secondary" className="bg-primary/20 text-primary-foreground border-primary/30">
                    {character.class}
                  </Badge>
                  <Badge variant="outline" className="border-accent/50 text-accent-foreground">
                    Уровень {character.level}
                  </Badge>
                </div>
              </div>

              {/* HP Bar */}
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm">
                  <Heart className="w-4 h-4 text-red-600" />
                  <span className="font-medium text-foreground">
                    {character.hp} / {character.maxHp} HP
                  </span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-red-600 to-red-500 transition-all"
                    style={{ width: `${(character.hp / character.maxHp) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="mt-4 grid grid-cols-3 gap-2">
            <StatBox icon={Sword} label="СИЛ" value={character.stats.str} />
            <StatBox icon={Zap} label="ЛОВ" value={character.stats.dex} />
            <StatBox icon={Shield} label="ТЕЛ" value={character.stats.con} />
            <StatBox icon={Brain} label="ИНТ" value={character.stats.int} />
            <StatBox icon={Users} label="МДР" value={character.stats.wis} />
            <StatBox icon={Heart} label="ХАР" value={character.stats.cha} />
          </div>
        </Card>
      ))}
    </div>
  )
}

function StatBox({ icon: Icon, label, value }: { icon: any; label: string; value: number }) {
  const modifier = Math.floor((value - 10) / 2)
  return (
    <div className="bg-muted/50 rounded-md p-2 text-center border border-border">
      <Icon className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
      <div className="text-xs text-muted-foreground font-medium">{label}</div>
      <div className="text-lg font-bold text-foreground">{value}</div>
      <div className="text-xs text-accent font-medium">
        {modifier >= 0 ? "+" : ""}
        {modifier}
      </div>
    </div>
  )
}
