import { useState, useRef, useEffect, useCallback } from 'react';
import type { Token as TokenType } from '../types/game';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { cn } from '@/lib/utils';

interface TokenProps {
  token: TokenType;
  canMove: boolean;
  onMove: (tokenId: string, x: number, y: number) => void;
  onClick?: () => void;
  isDead?: boolean;
  onDragStart?: () => void;
  mapRef?: React.RefObject<HTMLDivElement | null>;
  imgRef?: React.RefObject<HTMLImageElement | null>;
}

export default function Token({ token, canMove, onMove, onClick, isDead = false, onDragStart, mapRef, imgRef }: TokenProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState({ x: token.x, y: token.y });
  const tokenRef = useRef<HTMLDivElement>(null);
  const dragStartRef = useRef<{ x: number; y: number } | null>(null);
  const hasMovedRef = useRef(false);
  const animationFrameRef = useRef<number | null>(null);
  const lastPositionRef = useRef({ x: token.x, y: token.y });

  useEffect(() => {
    if (!isDragging) {
      setPosition({ x: token.x, y: token.y });
      lastPositionRef.current = { x: token.x, y: token.y };
    }
  }, [token.x, token.y, isDragging]);

  const handleMouseDown = (e: React.MouseEvent) => {
    hasMovedRef.current = false;
    if (!canMove) {
      // Если не может двигать, можно кликнуть
      if (onClick) {
        onClick();
      }
      return;
    }
    e.preventDefault();
    e.stopPropagation(); // Предотвращаем pan карты при перетаскивании токена
    setIsDragging(true);
    // Закрываем меню при начале перетаскивания
    if (onDragStart) {
      onDragStart();
    }
    const rect = tokenRef.current?.parentElement?.getBoundingClientRect();
    if (rect) {
      dragStartRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    }
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !canMove || !dragStartRef.current) return;
    
    // Отменяем предыдущий кадр анимации для плавности
    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    // Используем requestAnimationFrame для плавного обновления
    animationFrameRef.current = requestAnimationFrame(() => {
      // Находим контейнер карты (mapRef) для правильного расчета позиции
      const mapElement = mapRef?.current;
      const imgElement = imgRef?.current;
      
      if (!mapElement) {
        // Fallback: используем родительский элемент
        const parent = tokenRef.current?.parentElement?.parentElement;
        if (!parent) return;
        const rect = parent.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        const clampedX = Math.max(0, Math.min(100, x));
        const clampedY = Math.max(0, Math.min(100, y));
        
        // Уменьшенный порог для лучшей точности при малых перемещениях
        if (Math.abs(clampedX - lastPositionRef.current.x) > 0.1 || Math.abs(clampedY - lastPositionRef.current.y) > 0.1) {
          hasMovedRef.current = true;
        }
        
        setPosition({ x: clampedX, y: clampedY });
        lastPositionRef.current = { x: clampedX, y: clampedY };
        return;
      }

      // Получаем реальные размеры изображения карты
      const naturalWidth = imgElement?.naturalWidth || mapElement.offsetWidth;
      const naturalHeight = imgElement?.naturalHeight || mapElement.offsetHeight;
      
      // Получаем bounding rect карты (учитывает трансформации)
      const mapRect = mapElement.getBoundingClientRect();
      
      // Вычисляем позицию курсора относительно viewport карты
      const viewportX = e.clientX - mapRect.left;
      const viewportY = e.clientY - mapRect.top;
      
      // Преобразуем в проценты относительно реальных размеров карты
      // Это дает более точное позиционирование
      const x = (viewportX / mapRect.width) * 100;
      const y = (viewportY / mapRect.height) * 100;

      // Ограничиваем границы
      const clampedX = Math.max(0, Math.min(100, x));
      const clampedY = Math.max(0, Math.min(100, y));

      // Уменьшенный порог для лучшей точности при малых перемещениях (0.1% вместо 1%)
      if (Math.abs(clampedX - lastPositionRef.current.x) > 0.1 || Math.abs(clampedY - lastPositionRef.current.y) > 0.1) {
        hasMovedRef.current = true;
      }

      setPosition({ x: clampedX, y: clampedY });
      lastPositionRef.current = { x: clampedX, y: clampedY };
    });
  }, [isDragging, canMove, mapRef, imgRef]);

  const handleMouseUp = useCallback(() => {
    // Отменяем анимацию при отпускании
    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    if (isDragging && canMove && hasMovedRef.current) {
      // Используем lastPositionRef для актуальной позиции
      onMove(token.id, lastPositionRef.current.x, lastPositionRef.current.y);
    }
    // Убрали вызов onClick() - теперь меню открывается только при двойном клике
    setIsDragging(false);
    dragStartRef.current = null;
    hasMovedRef.current = false;
  }, [isDragging, canMove, token.id, onMove]);

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (onClick && !isDragging) {
      onClick();
    }
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove, { passive: true });
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        if (animationFrameRef.current !== null) {
          cancelAnimationFrame(animationFrameRef.current);
        }
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <button
      ref={tokenRef}
      className={cn(
        'group transition-all duration-150',
        canMove && !isDragging && 'cursor-move',
        isDragging && 'z-50 cursor-grabbing',
        !isDragging && 'z-10 cursor-pointer'
      )}
      onMouseDown={handleMouseDown}
      onDoubleClick={handleDoubleClick}
      disabled={!canMove && !onClick}
    >
      <div className="relative">
        <Avatar className={cn(
          'w-14 h-14 border-4 border-accent shadow-lg ring-4 ring-accent/30 transition-all duration-200',
          'group-hover:ring-accent/60 group-hover:scale-110',
          isDragging && 'scale-125 shadow-2xl ring-4 ring-primary/50 border-primary',
          isDead && 'opacity-75 grayscale-[0.3]'
        )}
        style={isDead ? {
          filter: 'sepia(0.5) saturate(1.5) hue-rotate(-10deg)',
          borderColor: 'hsl(var(--destructive))',
        } : undefined}
        >
          {token.image_url ? (
            <AvatarImage src={token.image_url} alt={token.name} />
          ) : null}
          <AvatarFallback className="bg-primary text-primary-foreground font-bold">
            {token.name[0].toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap bg-card/95 px-2 py-0.5 rounded border border-border text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          {token.name}
        </div>
      </div>
    </button>
  );
}

