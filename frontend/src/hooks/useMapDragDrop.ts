import { useState, useEffect, RefObject } from 'react';
import type { Character } from '../types/character';
import { useGameStore } from '../store/gameStore';
import { useAuthStore } from '../store/authStore';
import { socketService } from '../services/socket';

export interface DraggableNPC {
  slug: string;
  name: string;
}

interface UseMapDragDropOptions {
  gameId: string;
  characters: Character[];
  npcMonsters?: DraggableNPC[];
  canMoveTokens: boolean;
  mapRef: RefObject<HTMLDivElement | null>;
  setIsHeroesPopoverOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export function useMapDragDrop({
  gameId,
  characters,
  npcMonsters = [],
  canMoveTokens,
  mapRef,
  setIsHeroesPopoverOpen,
}: UseMapDragDropOptions) {
  const [draggedCharacter, setDraggedCharacter] = useState<Character | null>(null);
  const [draggedNPC, setDraggedNPC] = useState<DraggableNPC | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleCharacterDragStart = (character: Character) => {
    setDraggedCharacter(character);
    setDraggedNPC(null);
    setIsDragging(true);
  };

  const handleNPCDragStart = (npc: DraggableNPC) => {
    setDraggedNPC(npc);
    setDraggedCharacter(null);
    setIsDragging(true);
  };

  useEffect(() => {
    const mapElement = mapRef.current;
    if (!mapElement) return;

    const handleDrop = (e: DragEvent) => {
      const target = e.target as HTMLElement;
      const isOnMap =
        mapElement.contains(target) ||
        target === mapElement ||
        (e.target as HTMLElement)?.closest('.relative') === mapElement;

      if (!isOnMap) return;

      e.preventDefault();
      e.stopPropagation();

      if (!canMoveTokens) {
        setDraggedCharacter(null);
        setDraggedNPC(null);
        setIsDragging(false);
        return;
      }

      const rect = mapElement.getBoundingClientRect();
      const clampedX = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
      const clampedY = Math.max(0, Math.min(100, ((e.clientY - rect.top) / rect.height) * 100));

      const entityType = e.dataTransfer?.getData('entity-type');

      if (entityType === 'npc') {
        const slug = e.dataTransfer?.getData('npc-slug');
        const npc = draggedNPC || npcMonsters.find(m => m.slug === slug);
        if (npc) {
          const tempToken = {
            id: `temp-${Date.now()}`,
            game_id: gameId,
            name: npc.name,
            x: clampedX,
            y: clampedY,
            image_url: null,
            is_hidden: false,
            token_type: 'npc' as const,
            token_metadata: { monster_slug: npc.slug },
          };
          useGameStore.getState().addToken(tempToken);
          socketService.createToken(gameId, npc.name, clampedX, clampedY, undefined, 'npc');
        }
        setDraggedNPC(null);
        setIsDragging(false);
        return;
      }

      // Hero / character drop
      const characterId = e.dataTransfer?.getData('text/plain');
      const character = draggedCharacter || characters.find(c => c.id === characterId);

      if (!character) {
        setDraggedCharacter(null);
        setIsDragging(false);
        return;
      }

      const socket = socketService.getSocket();
      if (!socket || !socket.connected) {
        const { token } = useAuthStore.getState();
        if (token) {
          socketService.connect(token);
          socketService.joinGame(gameId);
          setTimeout(() => {
            socketService.createToken(gameId, character.name, clampedX, clampedY, character.avatar_url || undefined, 'player');
          }, 500);
        }
        setDraggedCharacter(null);
        setIsDragging(false);
        return;
      }

      const tempToken = {
        id: `temp-${Date.now()}`,
        game_id: gameId,
        name: character.name,
        x: clampedX,
        y: clampedY,
        image_url: character.avatar_url || null,
        is_hidden: false,
        token_type: 'player' as const,
        token_metadata: null,
      };
      useGameStore.getState().addToken(tempToken);
      socketService.createToken(gameId, character.name, clampedX, clampedY, character.avatar_url || undefined, 'player');

      setDraggedCharacter(null);
      setIsDragging(false);
      setIsHeroesPopoverOpen(false);
    };

    const handleDragOver = (e: DragEvent) => {
      const target = e.target as HTMLElement;
      const isOnMap =
        mapElement.contains(target) ||
        target === mapElement ||
        (e.target as HTMLElement)?.closest('.relative') === mapElement;
      if (!isOnMap) return;
      e.preventDefault();
      e.stopPropagation();
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
    };

    const handleDragEnter = (e: DragEvent) => {
      const target = e.target as HTMLElement;
      const isOnMap =
        mapElement.contains(target) ||
        target === mapElement ||
        (e.target as HTMLElement)?.closest('.relative') === mapElement;
      if (!isOnMap) return;
      e.preventDefault();
      e.stopPropagation();
    };

    document.addEventListener('drop', handleDrop, true);
    document.addEventListener('dragover', handleDragOver, true);
    document.addEventListener('dragenter', handleDragEnter, true);
    mapElement.addEventListener('drop', handleDrop, true);
    mapElement.addEventListener('dragover', handleDragOver, true);
    mapElement.addEventListener('dragenter', handleDragEnter, true);

    return () => {
      mapElement.removeEventListener('drop', handleDrop, true);
      mapElement.removeEventListener('dragover', handleDragOver, true);
      mapElement.removeEventListener('dragenter', handleDragEnter, true);
      document.removeEventListener('drop', handleDrop, true);
      document.removeEventListener('dragover', handleDragOver, true);
      document.removeEventListener('dragenter', handleDragEnter, true);
    };
  }, [draggedCharacter, draggedNPC, characters, npcMonsters, canMoveTokens, gameId, isDragging]);

  return {
    draggedCharacter,
    draggedNPC,
    isDragging,
    setDraggedCharacter,
    setDraggedNPC,
    setIsDragging,
    handleCharacterDragStart,
    handleNPCDragStart,
  };
}
