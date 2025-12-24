"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Save, Scroll } from "lucide-react"

interface CharacterData {
  name: string
  race: string
  class: string
  level: number
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
  lore: string
  notes: string
}

export default function CharacterCreation() {
  const router = useRouter()
  const [character, setCharacter] = useState<CharacterData>({
    name: "",
    race: "",
    class: "",
    level: 1,
    strength: 10,
    dexterity: 10,
    constitution: 10,
    intelligence: 10,
    wisdom: 10,
    charisma: 10,
    lore: "",
    notes: "",
  })

  const handleSave = () => {
    console.log("[v0] Saving character:", character)
    router.push("/")
  }

  const updateField = (field: keyof CharacterData, value: string | number) => {
    setCharacter((prev) => ({ ...prev, [field]: value }))
  }

  const getModifier = (score: number) => {
    const mod = Math.floor((score - 10) / 2)
    return mod >= 0 ? `+${mod}` : `${mod}`
  }

  return (
    <div className="min-h-screen bg-[#f4e8d8] p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 text-center">
          <div className="inline-block relative">
            <div className="absolute inset-0 bg-gradient-to-r from-[#8b4513]/20 via-transparent to-[#8b4513]/20 blur-xl" />
            <h1 className="relative font-serif text-4xl md:text-5xl text-[#5c3317] tracking-wide px-8 py-4 border-t-4 border-b-4 border-[#8b4513] bg-[#f4e8d8]">
              Создание персонажа
            </h1>
          </div>
          <div className="mt-2 flex items-center justify-center gap-2 text-[#8b4513]">
            <div className="h-px w-16 bg-gradient-to-r from-transparent to-[#8b4513]" />
            <Scroll className="w-5 h-5" />
            <div className="h-px w-16 bg-gradient-to-l from-transparent to-[#8b4513]" />
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card className="bg-[#faf6f0] border-4 border-[#8b4513] shadow-2xl p-6 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-16 h-16 border-t-4 border-l-4 border-[#d4af37] opacity-50" />
              <div className="absolute top-0 right-0 w-16 h-16 border-t-4 border-r-4 border-[#d4af37] opacity-50" />
              <div className="absolute bottom-0 left-0 w-16 h-16 border-b-4 border-l-4 border-[#d4af37] opacity-50" />
              <div className="absolute bottom-0 right-0 w-16 h-16 border-b-4 border-r-4 border-[#d4af37] opacity-50" />

              <div className="bg-[#f4e8d8] border-2 border-[#8b4513] rounded p-4 mb-6 shadow-inner">
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <Label className="text-sm font-bold text-[#5c3317] uppercase tracking-wider mb-2 block">
                      Имя персонажа
                    </Label>
                    <Input
                      value={character.name}
                      onChange={(e) => updateField("name", e.target.value)}
                      className="bg-[#faf6f0] border-2 border-[#8b4513] font-serif text-lg"
                      placeholder="Введите имя героя"
                    />
                  </div>
                  <div>
                    <Label className="text-sm font-bold text-[#5c3317] uppercase tracking-wider mb-2 block">Раса</Label>
                    <Input
                      value={character.race}
                      onChange={(e) => updateField("race", e.target.value)}
                      className="bg-[#faf6f0] border-2 border-[#8b4513] font-serif"
                      placeholder="Человек, эльф, дворф..."
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-bold text-[#5c3317] uppercase tracking-wider mb-2 block">
                      Класс
                    </Label>
                    <Input
                      value={character.class}
                      onChange={(e) => updateField("class", e.target.value)}
                      className="bg-[#faf6f0] border-2 border-[#8b4513] font-serif"
                      placeholder="Воин, маг, плут..."
                    />
                  </div>
                  <div>
                    <Label className="text-sm font-bold text-[#5c3317] uppercase tracking-wider mb-2 block">
                      Уровень
                    </Label>
                    <Input
                      type="number"
                      value={character.level}
                      onChange={(e) => updateField("level", Number.parseInt(e.target.value) || 1)}
                      className="bg-[#faf6f0] border-2 border-[#8b4513] font-serif text-center text-xl font-bold"
                      min="1"
                      max="20"
                    />
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-lg font-bold text-[#5c3317] uppercase tracking-wider mb-4 pb-2 border-b-2 border-[#8b4513] flex items-center gap-2">
                  <span className="text-[#d4af37]">⚔</span> Характеристики
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {[
                    { key: "strength", label: "Сила" },
                    { key: "dexterity", label: "Ловкость" },
                    { key: "constitution", label: "Телосложение" },
                    { key: "intelligence", label: "Интеллект" },
                    { key: "wisdom", label: "Мудрость" },
                    { key: "charisma", label: "Харизма" },
                  ].map((stat) => (
                    <div key={stat.key} className="bg-[#f4e8d8] border-2 border-[#8b4513] rounded p-3 shadow-md">
                      <Label className="text-xs font-bold text-[#5c3317] uppercase tracking-wide mb-2 block text-center">
                        {stat.label}
                      </Label>
                      <div className="flex items-center justify-center gap-2">
                        <Input
                          type="number"
                          value={character[stat.key as keyof CharacterData]}
                          onChange={(e) =>
                            updateField(stat.key as keyof CharacterData, Number.parseInt(e.target.value) || 10)
                          }
                          className="w-16 h-16 text-center font-bold text-2xl border-2 border-[#8b4513] bg-[#faf6f0] rounded-full"
                          min="1"
                          max="20"
                        />
                        <div className="w-12 h-12 rounded-full bg-[#8b4513] flex items-center justify-center text-[#d4af37] font-bold text-lg shadow-md">
                          {getModifier(Number(character[stat.key as keyof CharacterData]))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-bold text-[#5c3317] uppercase tracking-wider mb-2 block flex items-center gap-2">
                    <span className="text-[#d4af37]">📜</span> История персонажа
                  </Label>
                  <Textarea
                    value={character.lore}
                    onChange={(e) => updateField("lore", e.target.value)}
                    className="bg-[#faf6f0] border-2 border-[#8b4513] min-h-32 font-serif text-[#5c3317]"
                    placeholder="Расскажите историю вашего героя..."
                  />
                </div>

                <div>
                  <Label className="text-sm font-bold text-[#5c3317] uppercase tracking-wider mb-2 block flex items-center gap-2">
                    <span className="text-[#d4af37]">⚔️</span> Снаряжение и особенности
                  </Label>
                  <Textarea
                    value={character.notes}
                    onChange={(e) => updateField("notes", e.target.value)}
                    className="bg-[#faf6f0] border-2 border-[#8b4513] min-h-24 font-serif text-[#5c3317]"
                    placeholder="Оружие, доспехи, особые предметы..."
                  />
                </div>
              </div>
            </Card>

            <div className="flex gap-4 mt-6">
              <Button
                onClick={() => router.push("/")}
                variant="outline"
                className="flex-1 border-3 border-[#8b4513] text-[#5c3317] hover:bg-[#8b4513] hover:text-[#faf6f0] font-bold py-6 text-lg bg-[#f4e8d8]"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Вернуться в лобби
              </Button>
              <Button
                onClick={handleSave}
                className="flex-1 bg-[#8b4513] hover:bg-[#5c3317] text-[#faf6f0] font-bold py-6 text-lg shadow-lg border-2 border-[#5c3317]"
              >
                <Save className="w-5 h-5 mr-2" />
                Сохранить персонажа
              </Button>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <h3 className="text-xl font-bold text-[#5c3317] mb-4 uppercase tracking-wide text-center">
                Предпросмотр
              </h3>
              <Card className="bg-[#faf6f0] border-4 border-[#8b4513] shadow-2xl p-6 relative">
                <div className="absolute top-0 left-0 w-12 h-12 border-t-2 border-l-2 border-[#d4af37]" />
                <div className="absolute top-0 right-0 w-12 h-12 border-t-2 border-r-2 border-[#d4af37]" />
                <div className="absolute bottom-0 left-0 w-12 h-12 border-b-2 border-l-2 border-[#d4af37]" />
                <div className="absolute bottom-0 right-0 w-12 h-12 border-b-2 border-r-2 border-[#d4af37]" />

                <div className="text-center space-y-4">
                  <div className="w-32 h-32 mx-auto bg-gradient-to-br from-[#8b4513] to-[#5c3317] rounded-full flex items-center justify-center border-4 border-[#d4af37] shadow-xl">
                    <span className="text-6xl text-[#faf6f0] font-bold font-serif">
                      {character.name ? character.name[0].toUpperCase() : "?"}
                    </span>
                  </div>

                  <div className="border-t-2 border-b-2 border-[#8b4513] py-3">
                    <h4 className="font-serif text-2xl text-[#5c3317] font-bold">{character.name || "Имя героя"}</h4>
                    <p className="text-[#8b4513] font-semibold mt-1">
                      {character.class || "Класс"} • Уровень {character.level}
                    </p>
                    <p className="text-sm text-[#8b4513] italic">{character.race || "Раса"}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-2">
                    {[
                      { label: "Сила", value: character.strength },
                      { label: "Ловкость", value: character.dexterity },
                      { label: "Телосложение", value: character.constitution },
                      { label: "Интеллект", value: character.intelligence },
                      { label: "Мудрость", value: character.wisdom },
                      { label: "Харизма", value: character.charisma },
                    ].map((stat) => (
                      <div key={stat.label} className="bg-[#f4e8d8] border-2 border-[#8b4513] rounded p-2">
                        <div className="text-xs text-[#5c3317] font-bold uppercase">{stat.label}</div>
                        <div className="text-2xl font-bold text-[#8b4513]">{stat.value}</div>
                        <div className="text-sm text-[#d4af37] font-semibold">{getModifier(stat.value)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
