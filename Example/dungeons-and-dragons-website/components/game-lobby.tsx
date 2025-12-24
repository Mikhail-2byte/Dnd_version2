"use client"

import { useState } from "react"
import { Header } from "./header"
import { PlayerSidebar } from "./player-sidebar"
import { GameMap } from "./game-map"
import { CharacterPanel } from "./character-panel"

export function GameLobby() {
  const [activeTab, setActiveTab] = useState<"lobby" | "maps" | "characters">("lobby")
  const [selectedCharacter, setSelectedCharacter] = useState<string | null>(null)

  return (
    <div className="min-h-screen flex flex-col parchment-bg">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="flex-1 flex gap-4 p-4 max-w-[1800px] mx-auto w-full">
        {/* Player Sidebar */}
        <PlayerSidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col gap-4">
          {activeTab === "lobby" && <GameMap onCharacterSelect={setSelectedCharacter} />}
          {activeTab === "characters" && <CharacterPanel selectedId={selectedCharacter} />}
          {activeTab === "maps" && (
            <div className="flex-1 rounded-lg border-2 border-border bg-card p-8 flex items-center justify-center">
              <p className="text-muted-foreground text-lg">Map selection coming soon...</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
