import { useState, useEffect, RefObject } from 'react';
import type { Character } from '../types/character';
import { useGameStore } from '../store/gameStore';
import { useAuthStore } from '../store/authStore';
import { socketService } from '../services/socket';

interface UseMapDragDropOptions {
  gameId: string;
  characters: Character[];
  canMoveTokens: boolean;
  mapRef: RefObject<HTMLDivElement | null>;
  setIsHeroesPopoverOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export function useMapDragDrop({
  gameId,
  characters,
  canMoveTokens,
  mapRef,
  setIsHeroesPopoverOpen,
}: UseMapDragDropOptions) {
  const [draggedCharacter, setDraggedCharacter] = useState<Character | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleCharacterDragStart = (character: Character) => {
    console.log('Drag start:', character.name);
    setDraggedCharacter(character);
    setIsDragging(true);
  };

  useEffect(() => {
    const mapElement = mapRef.current;
    if (!mapElement) {
      console.log('Map element not found');
      return;
    }

    console.log('Setting up drag and drop handlers, isDragging:', isDragging);

    const handleDrop = (e: DragEvent) => {
      console.log('Drop event fired', {
        target: e.target,
        mapElement,
        isDragging,
        draggedCharacter,
        canMoveTokens,
      });

      const target = e.target as HTMLElement;
      const isOnMap = mapElement.contains(target) || target === mapElement ||
                      mapElement.contains(e.target as Node) ||
                      (e.target as HTMLElement)?.closest('.relative') === mapElement;

      if (!isOnMap) {
        console.log('Drop not on map, ignoring');
        return;
      }

      e.preventDefault();
      e.stopPropagation();

      const characterId = e.dataTransfer?.getData('text/plain');
      console.log('Character ID from dataTransfer:', characterId);

      const character = draggedCharacter || characters.find(c => c.id === characterId);

      if (!character) {
        console.warn('Character not found:', { characterId, draggedCharacter, characters: characters.length });
        setDraggedCharacter(null);
        setIsDragging(false);
        return;
      }

      if (!canMoveTokens) {
        console.warn('Cannot create token: not master');
        setDraggedCharacter(null);
        setIsDragging(false);
        return;
      }

      const rect = mapElement.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;

      const clampedX = Math.max(0, Math.min(100, x));
      const clampedY = Math.max(0, Math.min(100, y));

      console.log('Creating token (native):', {
        name: character.name,
        x: clampedX,
        y: clampedY,
        imageUrl: character.avatar_url,
        rect: { width: rect.width, height: rect.height },
        clientPos: { x: e.clientX, y: e.clientY },
      });

      const socket = socketService.getSocket();
      if (!socket || !socket.connected) {
        console.error('Socket not available, attempting to reconnect...');
        const { token } = useAuthStore.getState();
        if (token) {
          console.log('Reconnecting socket...');
          socketService.connect(token);
          socketService.joinGame(gameId);
          setTimeout(() => {
            socketService.createToken(
              gameId,
              character.name,
              clampedX,
              clampedY,
              character.avatar_url || undefined
            );
          }, 500);
          return;
        } else {
          console.error('No token available for reconnection');
          return;
        }
      }

      const tempTokenId = `temp-${Date.now()}`;
      const tempToken = {
        id: tempTokenId,
        game_id: gameId,
        name: character.name,
        x: clampedX,
        y: clampedY,
        image_url: character.avatar_url || null,
      };
      console.log('Adding temporary token to store:', tempToken);
      useGameStore.getState().addToken(tempToken);

      socketService.createToken(
        gameId,
        character.name,
        clampedX,
        clampedY,
        character.avatar_url || undefined
      );

      setDraggedCharacter(null);
      setIsDragging(false);
      setIsHeroesPopoverOpen(false);
    };

    const handleDragOver = (e: DragEvent) => {
      const target = e.target as HTMLElement;
      const isOnMap = mapElement.contains(target) || target === mapElement ||
                      mapElement.contains(e.target as Node) ||
                      (e.target as HTMLElement)?.closest('.relative') === mapElement;

      if (!isOnMap) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = 'move';
      }
    };

    const handleDragEnter = (e: DragEvent) => {
      const target = e.target as HTMLElement;
      const isOnMap = mapElement.contains(target) || target === mapElement ||
                      mapElement.contains(e.target as Node) ||
                      (e.target as HTMLElement)?.closest('.relative') === mapElement;

      if (!isOnMap) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      console.log('Drag enter on map');
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
  }, [draggedCharacter, characters, canMoveTokens, gameId, isDragging]);

  return { draggedCharacter, isDragging, setDraggedCharacter, setIsDragging, handleCharacterDragStart };
}
