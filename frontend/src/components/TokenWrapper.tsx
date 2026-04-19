import { useState, useEffect } from 'react';
import { Popover, PopoverContent, PopoverAnchor } from './ui/popover';
import { Button } from './ui/button';
import { Trash2, Skull, Heart } from 'lucide-react';
import Token from './Token';

export interface TokenWrapperProps {
  token: any;
  canMoveTokens: boolean;
  selectedTokenId: string | null;
  isDead: boolean;
  mapRef: React.RefObject<HTMLDivElement | null>;
  imgRef: React.RefObject<HTMLImageElement | null>;
  onTokenClick: (tokenId: string) => void;
  onTokenMove: (tokenId: string, x: number, y: number) => void;
  onTokenDelete: (tokenId: string) => void;
  onTokenToggleDead: (tokenId: string) => void;
  onSelectChange: (tokenId: string | null) => void;
}

export default function TokenWrapper({
  token,
  canMoveTokens,
  selectedTokenId,
  isDead,
  mapRef,
  imgRef,
  onTokenClick,
  onTokenMove,
  onTokenDelete,
  onTokenToggleDead,
  onSelectChange,
}: TokenWrapperProps) {
  const [tokenPosition, setTokenPosition] = useState({ x: token.x, y: token.y });

  useEffect(() => {
    setTokenPosition({ x: token.x, y: token.y });
  }, [token.x, token.y]);

  const handleMove = (tokenId: string, x: number, y: number) => {
    setTokenPosition({ x, y });
    onTokenMove(tokenId, x, y);
  };

  return (
    <Popover
      open={selectedTokenId === token.id && canMoveTokens}
      onOpenChange={(open) => {
        if (!open) onSelectChange(null);
      }}
    >
      <PopoverAnchor asChild>
        <div
          className="absolute group"
          style={{
            left: `${tokenPosition.x}%`,
            top: `${tokenPosition.y}%`,
            transform: 'translate(-50%, -50%)',
            zIndex: selectedTokenId === token.id ? 50 : 10,
          }}
        >
          <Token
            token={token}
            canMove={canMoveTokens}
            onMove={handleMove}
            onClick={() => onTokenClick(token.id)}
            isDead={isDead}
            onDragStart={() => onSelectChange(null)}
            mapRef={mapRef}
            imgRef={imgRef}
          />
        </div>
      </PopoverAnchor>
      {selectedTokenId === token.id && canMoveTokens && (
        <PopoverContent
          className="w-40 p-2"
          side="top"
          align="center"
          sideOffset={8}
        >
          <div className="flex flex-col gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10"
              onClick={(e) => {
                e.stopPropagation();
                onTokenDelete(token.id);
              }}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Удалить
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className={isDead
                ? "w-full justify-start text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-950"
                : "w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10"
              }
              onClick={(e) => {
                e.stopPropagation();
                onTokenToggleDead(token.id);
              }}
            >
              {isDead ? (
                <>
                  <Heart className="w-4 h-4 mr-2" />
                  Воскресить
                </>
              ) : (
                <>
                  <Skull className="w-4 h-4 mr-2" />
                  Убитый
                </>
              )}
            </Button>
          </div>
        </PopoverContent>
      )}
    </Popover>
  );
}
