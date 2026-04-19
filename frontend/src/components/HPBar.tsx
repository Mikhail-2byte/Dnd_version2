interface HPBarProps {
  current: number;
  max: number;
  showText?: boolean;
  className?: string;
}

export default function HPBar({ current, max, showText = true, className = '' }: HPBarProps) {
  const percentage = max > 0 ? Math.max(0, Math.min(100, (current / max) * 100)) : 0;
  
  // Определяем цвет в зависимости от процента HP
  let bgColor = '';
  if (percentage >= 50) {
    bgColor = 'rgb(34, 197, 94)'; // green-500
  } else if (percentage >= 25) {
    bgColor = 'rgb(234, 179, 8)'; // yellow-500
  } else {
    bgColor = 'rgb(239, 68, 68)'; // red-500
  }
  
  return (
    <div className={`w-full ${className}`}>
      {showText && (
        <div className="flex justify-between items-center mb-1 text-sm">
          <span className="font-medium">{current}/{max} HP</span>
          <span className="text-muted-foreground">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{ 
            width: `${percentage}%`,
            backgroundColor: bgColor
          }}
        />
      </div>
    </div>
  );
}

