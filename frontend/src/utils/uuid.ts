/**
 * Утилиты для работы с UUID
 */

/**
 * Проверяет, является ли строка валидным UUID
 */
export function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

/**
 * Проверяет, является ли персонаж шаблонным
 */
export function isTemplateCharacter(characterId: string): boolean {
  return characterId.startsWith('template-') || !isValidUUID(characterId);
}
