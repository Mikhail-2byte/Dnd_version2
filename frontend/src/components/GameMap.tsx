import { useRef, useState } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { useGameStore } from '../store/gameStore';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { ZoomIn, ZoomOut, RotateCcw, Maximize2, Users } from 'lucide-react';
import type { Character } from '../types/character';
import TokenWrapper from './TokenWrapper';
import { useTokenHandlers } from '../hooks/useTokenHandlers';
import { useMapDragDrop } from '../hooks/useMapDragDrop';

interface GameMapProps {
  gameId: string;
  characters?: Character[];
}

export default function GameMap({ gameId, characters = [] }: GameMapProps) {
  const { currentGame, tokens, currentUserRole } = useGameStore();
  const mapRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const transformRef = useRef<any>(null);
  const initialScaleRef = useRef(0.33);
  const [zoomLevel, setZoomLevel] = useState(0.33);
  const [isHeroesPopoverOpen, setIsHeroesPopoverOpen] = useState(false);
  const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null);
  const [deadTokens, setDeadTokens] = useState<Set<string>>(new Set());

  const canMoveTokens = currentUserRole === 'master';

  const { handleTokenMove, handleTokenClick, handleDeleteToken, handleToggleDead } =
    useTokenHandlers({ gameId, canMoveTokens, tokens, setDeadTokens, setSelectedTokenId });

  const { isDragging, setDraggedCharacter, setIsDragging, handleCharacterDragStart } =
    useMapDragDrop({ gameId, characters, canMoveTokens, mapRef, setIsHeroesPopoverOpen });

  const availableCharacters = characters.filter((character) => {
    return !tokens.some((token) => token.name === character.name);
  });

  const mapUrl = currentGame?.map_url || '/assets/images/default-map.jpg';

  const resetToInitialView = () => {
    if (transformRef.current && mapRef.current) {
      const container = mapRef.current.parentElement?.parentElement;
      if (container) {
        const containerRect = container.getBoundingClientRect();
        const mapWidth = mapRef.current.offsetWidth;
        const mapHeight = mapRef.current.offsetHeight;
        const scale = initialScaleRef.current;
        const centerX = containerRect.width / 2 - (mapWidth * scale) / 2;
        const centerY = containerRect.height / 2 - (mapHeight * scale) / 2;
        transformRef.current.setTransform(centerX, centerY, scale);
        setZoomLevel(scale);
      }
    }
  };

  return (
    <Card className="flex-1 border-2 border-border bg-card/95 backdrop-blur-sm overflow-hidden p-0 h-full relative" style={{ overflow: 'hidden' }}>
      <TransformWrapper
        ref={transformRef}
        initialScale={0.33}
        minScale={0.1}
        maxScale={3}
        initialPositionX={0}
        initialPositionY={0}
        centerOnInit={false}
        limitToBounds={false}
        wheel={{ step: 0.1 }}
        doubleClick={{ disabled: true }}
        panning={{
          disabled: isDragging,
          lockAxisX: false,
          lockAxisY: false,
        }}
        onTransformed={(_, state) => {
          setZoomLevel(state.scale);
        }}
      >
        {({ zoomIn, zoomOut, centerView }) => (
          <>
            {/* Кнопки управления zoom */}
            <div className="absolute top-4 right-4 z-50 flex flex-col gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => zoomIn()}
                className="bg-card/90 backdrop-blur-sm border-2"
                title="Приблизить"
              >
                <ZoomIn className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => zoomOut()}
                className="bg-card/90 backdrop-blur-sm border-2"
                title="Отдалить"
              >
                <ZoomOut className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => resetToInitialView()}
                className="bg-card/90 backdrop-blur-sm border-2"
                title="Сбросить"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => centerView()}
                className="bg-card/90 backdrop-blur-sm border-2"
                title="Центрировать"
              >
                <Maximize2 className="w-4 h-4" />
              </Button>
            </div>

            {/* Информационный блок с названием карты */}
            <div className="absolute top-4 left-4 z-50 flex flex-col gap-2">
              {currentGame?.name && (
                <div className="bg-card/90 backdrop-blur-sm border-2 border-border rounded-lg p-3 shadow-lg pointer-events-none">
                  <h3 className="font-bold text-sm text-foreground mb-1">{currentGame.name}</h3>
                  <p className="text-xs text-muted-foreground">
                    {currentGame.story ? currentGame.story.substring(0, 50) + '...' : 'Игровая сессия'}
                  </p>
                </div>
              )}
              <div className="bg-card/90 backdrop-blur-sm border-2 border-border rounded-lg px-3 py-1.5 shadow-lg">
                <span className="text-xs font-medium text-foreground">
                  Zoom: {Math.round(zoomLevel * 100)}%
                </span>
              </div>
              {canMoveTokens && (
                <Popover open={isHeroesPopoverOpen} onOpenChange={setIsHeroesPopoverOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="bg-card/90 backdrop-blur-sm border-2 border-border w-full justify-start"
                    >
                      <Users className="w-4 h-4 mr-2" />
                      Герои
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-64 p-2" align="start">
                    {availableCharacters.length === 0 ? (
                      <div className="text-sm text-muted-foreground text-center py-4">
                        Все герои уже на карте
                      </div>
                    ) : (
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {availableCharacters.map((character) => (
                          <div
                            key={character.id}
                            draggable
                            onDragStart={(e) => {
                              handleCharacterDragStart(character);
                              e.dataTransfer.effectAllowed = 'move';
                              e.dataTransfer.setData('text/plain', character.id);
                            }}
                            onDragEnd={() => {
                              setDraggedCharacter(null);
                              setIsDragging(false);
                            }}
                            className="flex items-center gap-3 p-2 rounded-lg border-2 border-border bg-card/95 backdrop-blur-sm cursor-move hover:bg-card hover:shadow-md transition-all active:opacity-50"
                          >
                            <Avatar className="w-10 h-10 border-2 border-accent">
                              {character.avatar_url ? (
                                <AvatarImage src={character.avatar_url} alt={character.name} />
                              ) : null}
                              <AvatarFallback className="bg-primary text-primary-foreground font-bold">
                                {character.name[0].toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-foreground truncate">
                                {character.name}
                              </p>
                              <p className="text-xs text-muted-foreground truncate">
                                {character.race} • {character.class}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </PopoverContent>
                </Popover>
              )}
            </div>

            <TransformComponent
              wrapperClass="w-full h-full overflow-hidden"
              contentClass=""
            >
              <div
                ref={mapRef}
                className="relative"
                style={{
                  pointerEvents: 'auto',
                  touchAction: 'none',
                }}
              >
                <img
                  ref={imgRef}
                  src={mapUrl}
                  alt="Game Map"
                  className="block"
                  style={{ display: 'block' }}
                  onLoad={(e) => {
                    const img = e.target as HTMLImageElement;
                    if (img && mapRef.current && transformRef.current) {
                      const naturalWidth = img.naturalWidth || 1000;
                      const naturalHeight = img.naturalHeight || 1000;
                      img.style.width = `${naturalWidth}px`;
                      img.style.height = `${naturalHeight}px`;
                      img.style.display = 'block';
                      mapRef.current.style.width = `${naturalWidth}px`;
                      mapRef.current.style.height = `${naturalHeight}px`;

                      const container = mapRef.current.parentElement?.parentElement;
                      if (container) {
                        const containerRect = container.getBoundingClientRect();
                        const scaleX = containerRect.width / naturalWidth;
                        const scaleY = containerRect.height / naturalHeight;
                        const fitScale = Math.min(scaleX, scaleY);
                        const initialScale = Math.min(0.33, fitScale * 0.9);
                        initialScaleRef.current = initialScale;

                        setTimeout(() => {
                          if (transformRef.current) {
                            const centerX = containerRect.width / 2 - (naturalWidth * initialScale) / 2;
                            const centerY = containerRect.height / 2 - (naturalHeight * initialScale) / 2;
                            transformRef.current.setTransform(centerX, centerY, initialScale);
                            setZoomLevel(initialScale);
                          }
                        }, 100);
                      }
                    }
                  }}
                />

                {/* Grid Overlay */}
                <div
                  className="absolute inset-0 opacity-20 pointer-events-none"
                  style={{
                    backgroundImage: `
                      linear-gradient(to right, hsl(var(--border)) 1px, transparent 1px),
                      linear-gradient(to bottom, hsl(var(--border)) 1px, transparent 1px)
                    `,
                    backgroundSize: '40px 40px',
                  }}
                />

                {/* Токены */}
                {tokens.map((token) => (
                  <TokenWrapper
                    key={token.id}
                    token={token}
                    canMoveTokens={canMoveTokens}
                    selectedTokenId={selectedTokenId}
                    isDead={deadTokens.has(token.id)}
                    mapRef={mapRef}
                    imgRef={imgRef}
                    onTokenClick={handleTokenClick}
                    onTokenMove={handleTokenMove}
                    onTokenDelete={handleDeleteToken}
                    onTokenToggleDead={handleToggleDead}
                    onSelectChange={setSelectedTokenId}
                  />
                ))}
              </div>
            </TransformComponent>
          </>
        )}
      </TransformWrapper>
    </Card>
  );
}
