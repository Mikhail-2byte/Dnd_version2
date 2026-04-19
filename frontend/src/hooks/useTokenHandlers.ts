import { useGameStore } from '../store/gameStore';
import { socketService } from '../services/socket';

interface UseTokenHandlersOptions {
  gameId: string;
  canMoveTokens: boolean;
  tokens: ReturnType<typeof useGameStore.getState>['tokens'];
  setDeadTokens: React.Dispatch<React.SetStateAction<Set<string>>>;
  setSelectedTokenId: React.Dispatch<React.SetStateAction<string | null>>;
}

export function useTokenHandlers({
  gameId,
  canMoveTokens,
  tokens,
  setDeadTokens,
  setSelectedTokenId,
}: UseTokenHandlersOptions) {
  const handleTokenMove = (tokenId: string, x: number, y: number) => {
    if (!canMoveTokens) return;
    useGameStore.getState().updateTokenPosition(tokenId, x, y);
    socketService.moveToken(gameId, tokenId, x, y);
  };

  const handleTokenClick = (tokenId: string) => {
    if (!canMoveTokens) return;
    setSelectedTokenId(tokenId);
  };

  const handleDeleteToken = (tokenId: string) => {
    if (!canMoveTokens) return;
    const token = tokens.find(t => t.id === tokenId);
    if (token) {
      console.log('Deleting token:', tokenId, token.name);
      setDeadTokens(prev => {
        const newSet = new Set(prev);
        newSet.delete(tokenId);
        return newSet;
      });
      useGameStore.getState().removeToken(tokenId);
      const socket = socketService.getSocket();
      if (socket && socket.connected) {
        socketService.deleteToken(gameId, tokenId);
        console.log('Delete token event emitted');
      } else {
        console.error('Socket not connected, cannot delete token');
      }
      setSelectedTokenId(null);
    }
  };

  const handleToggleDead = (tokenId: string) => {
    if (!canMoveTokens) return;
    setDeadTokens(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tokenId)) {
        newSet.delete(tokenId);
      } else {
        newSet.add(tokenId);
      }
      return newSet;
    });
    setSelectedTokenId(null);
  };

  return { handleTokenMove, handleTokenClick, handleDeleteToken, handleToggleDead };
}
