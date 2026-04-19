"""
Seed-скрипт для заполнения таблицы spells.
Данные взяты с https://dnd.su/spells/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.spell import Spell

SPELLS = [
    # ───────────── ЗАГОВОРЫ (УРОВЕНЬ 0) ─────────────
    {
        "slug": "fire-bolt", "name": "Огненный снаряд", "name_en": "Fire Bolt", "level": 0,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "120 футов",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Вы бросаете сгусток огня в существо или предмет в пределах дистанции. Совершите дальнобойную атаку заклинанием против цели. При попадании цель получает урон огнём 1d10. Горючие предметы, по которым попала атака и которые никто не несёт и не носит, воспламеняются. Урон заклинания возрастает на 1d10, когда вы достигаете 5-го (2d10), 11-го (3d10) и 17-го уровня (4d10).",
        "classes": ["wizard", "sorcerer", "artificer"],
    },
    {
        "slug": "mage-hand", "name": "Рука мага", "name_en": "Mage Hand", "level": 0,
        "school": "Conjuration", "casting_time": "1 действие", "spell_range": "30 футов",
        "components": {"v": True, "s": True},
        "duration": "1 минута", "concentration": False, "ritual": False,
        "description": "Парящая рука появляется в точке, которую вы можете видеть, в радиусе действия заклинания. Рука существует, пока действует заклинание. Бонусным действием вы можете управлять рукой. Рука не может атаковать, активировать магические предметы или нести больше 10 фунтов.",
        "classes": ["wizard", "sorcerer", "warlock", "bard", "artificer"],
    },
    {
        "slug": "eldritch-blast", "name": "Мистический снаряд", "name_en": "Eldritch Blast", "level": 0,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "120 футов",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Луч потрескивающей энергии устремляется к существу в пределах дистанции. Совершите дальнобойную атаку заклинанием против цели. При попадании цель получает урон силовым полем 1d10. Число лучей увеличивается: 2 луча (5 ур.), 3 луча (11 ур.), 4 луча (17 ур.). Каждый луч требует отдельного броска атаки.",
        "classes": ["warlock"],
    },
    {
        "slug": "sacred-flame", "name": "Священный огонь", "name_en": "Sacred Flame", "level": 0,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "60 футов",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Небесный огонь нисходит на существо в пределах дистанции. Цель должна успешно пройти спасбросок Ловкости, иначе получит урон излучением 1d8. Укрытие не даёт преимущества на этот спасбросок. Урон возрастает на 1d8 на 5-м (2d8), 11-м (3d8) и 17-м (4d8) уровнях.",
        "classes": ["cleric"],
    },
    {
        "slug": "vicious-mockery", "name": "Злая насмешка", "name_en": "Vicious Mockery", "level": 0,
        "school": "Enchantment", "casting_time": "1 действие", "spell_range": "60 футов",
        "components": {"v": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Вы обрушиваете на существо поток оскорблений, наполненных коварной магией. Если оно вас слышит и понимает (хотя бы частично), оно должно пройти спасбросок Мудрости. При провале цель получает урон психической энергией 1d4 и совершает следующий бросок атаки с помехой. Урон возрастает с уровнем.",
        "classes": ["bard"],
    },
    {
        "slug": "minor-illusion", "name": "Малая иллюзия", "name_en": "Minor Illusion", "level": 0,
        "school": "Illusion", "casting_time": "1 действие", "spell_range": "30 футов",
        "components": {"s": True, "m": "кусочек овечьей шерсти"},
        "duration": "1 минута", "concentration": False, "ritual": False,
        "description": "Вы создаёте звук или образ предмета в пределах дистанции, сохраняющийся на время действия заклинания. Созданный звук или изображение не касается иных чувств. Можно создать звук громкостью от шёпота до крика.",
        "classes": ["wizard", "sorcerer", "warlock", "bard"],
    },
    {
        "slug": "chill-touch", "name": "Ледяное прикосновение", "name_en": "Chill Touch", "level": 0,
        "school": "Necromancy", "casting_time": "1 действие", "spell_range": "120 футов",
        "components": {"v": True, "s": True},
        "duration": "1 раунд", "concentration": False, "ritual": False,
        "description": "Вы создаёте призрачную руку скелета в пространстве существа в пределах дистанции. Совершите дальнобойную атаку заклинанием против существа. При попадании цель получает 1d8 урона некротической энергией и до начала вашего следующего хода не может восстанавливать хиты. Если цель — нежить, она также совершает следующую атаку с помехой.",
        "classes": ["wizard", "sorcerer", "warlock", "cleric"],
    },
    {
        "slug": "guidance", "name": "Напутствие", "name_en": "Guidance", "level": 0,
        "school": "Divination", "casting_time": "1 действие", "spell_range": "Касание",
        "components": {"v": True, "s": True},
        "duration": "Концентрация, до 1 минуты", "concentration": True, "ritual": False,
        "description": "Вы касаетесь одного согласного существа. Один раз до конца действия заклинания цель может бросить d4 и добавить результат к одной проверке характеристики по своему выбору. Цель может совершить этот бросок до или после совершения проверки характеристики.",
        "classes": ["cleric", "druid", "artificer"],
    },
    {
        "slug": "ray-of-frost", "name": "Луч холода", "name_en": "Ray of Frost", "level": 0,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "60 футов",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Голубой луч холодного света устремляется к существу в пределах дистанции. Совершите дальнобойную атаку заклинанием против цели. При попадании цель получает урон холодом 1d8, и её скорость до начала вашего следующего хода уменьшается на 10 футов.",
        "classes": ["wizard", "sorcerer", "artificer"],
    },
    {
        "slug": "prestidigitation", "name": "Фокусничество", "name_en": "Prestidigitation", "level": 0,
        "school": "Transmutation", "casting_time": "1 действие", "spell_range": "10 футов",
        "components": {"v": True, "s": True},
        "duration": "До 1 часа", "concentration": False, "ritual": False,
        "description": "Это заклинание — трюк для начинающих волшебников, которые упражняются и практикуют основы магии. Вы создаёте один из следующих эффектов: безвредный сенсорный (искры, запах и т.д.), освещаете/тушите небольшой огонь, чистите или пачкаете предмет, охлаждаете/нагреваете, окрашиваете небольшой предмет.",
        "classes": ["wizard", "sorcerer", "warlock", "bard", "artificer"],
    },
    # ───────────── 1-й УРОВЕНЬ ─────────────
    {
        "slug": "magic-missile", "name": "Волшебная стрела", "name_en": "Magic Missile", "level": 1,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "120 футов",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Вы создаёте три светящихся дротика из магической силы. Каждый дротик поражает существо по вашему выбору, которое вы видите в пределах дистанции. Дротик наносит 1d4+1 урона силовым полем. Все дротики летят одновременно. При использовании ячейки 2-го уровня или выше заклинание создаёт ещё один дротик за каждый уровень ячейки выше первого.",
        "higher_levels": "При использовании ячейки 2-го уровня или выше — ещё один дротик за каждый уровень выше 1-го.",
        "classes": ["wizard", "sorcerer", "artificer"],
    },
    {
        "slug": "shield", "name": "Щит", "name_en": "Shield", "level": 1,
        "school": "Abjuration", "casting_time": "1 реакция (когда в вас целятся атакой или Волшебной стрелой)",
        "spell_range": "На себя",
        "components": {"v": True, "s": True},
        "duration": "1 раунд", "concentration": False, "ritual": False,
        "description": "Невидимый барьер магической силы появляется и защищает вас. До начала вашего следующего хода у вас есть бонус +5 к КБ, в том числе против атаки, вызвавшей применение этой реакции. Вы также не получаете урон от Волшебной стрелы.",
        "classes": ["wizard", "sorcerer", "artificer"],
    },
    {
        "slug": "cure-wounds", "name": "Лечение ран", "name_en": "Cure Wounds", "level": 1,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "Касание",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Существо, которого вы касаетесь, восстанавливает количество хитов, равное 1d8 + ваш модификатор заклинательной характеристики. Это заклинание не работает на нежить и конструкты.",
        "higher_levels": "При использовании ячейки 2-го уровня или выше количество восстанавливаемых хитов увеличивается на 1d8 за каждый уровень ячейки выше 1-го.",
        "classes": ["cleric", "druid", "paladin", "ranger", "bard", "artificer"],
    },
    {
        "slug": "healing-word", "name": "Слово исцеления", "name_en": "Healing Word", "level": 1,
        "school": "Evocation", "casting_time": "1 бонусное действие", "spell_range": "60 футов",
        "components": {"v": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Существо по вашему выбору, которое вы видите в пределах дистанции, восстанавливает количество хитов, равное 1d4 + ваш модификатор заклинательной характеристики. Это заклинание не работает на нежить и конструкты.",
        "higher_levels": "При использовании ячейки 2-го уровня или выше — ещё 1d4 за каждый уровень выше 1-го.",
        "classes": ["cleric", "druid", "bard"],
    },
    {
        "slug": "burning-hands", "name": "Горящие руки", "name_en": "Burning Hands", "level": 1,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "На себя (конус 15 футов)",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Когда вы разводите большие пальцы рук и растопыриваете пальцы, из кончиков ваших пальцев вырывается тонкий веер огня. Каждое существо в конусе 15 футов должно пройти спасбросок Ловкости. Существо получает урон огнём 3d6 при провале или половину при успехе. Огонь поджигает горючие предметы в этой области.",
        "higher_levels": "Урон возрастает на 1d6 за каждый уровень ячейки выше 1-го.",
        "classes": ["wizard", "sorcerer", "artificer"],
    },
    {
        "slug": "sleep", "name": "Сон", "name_en": "Sleep", "level": 1,
        "school": "Enchantment", "casting_time": "1 действие", "spell_range": "90 футов",
        "components": {"v": True, "s": True, "m": "щепотка мелкого песка, лепесток розы или сверчок"},
        "duration": "1 минута", "concentration": False, "ritual": False,
        "description": "Заклинание погружает существ в магический сон. Бросьте 5d8; результат — количество хитов существ, которых может усыпить заклинание. Существа в радиусе 20 футов от точки, начиная с наименее хитовых, погружаются в сон (при условии, что их хиты не превышают оставшееся число). Нежить и иммунные к очарованию существа не в счёт.",
        "higher_levels": "+2d8 к общей сумме хитов за каждый уровень ячейки выше 1-го.",
        "classes": ["wizard", "sorcerer", "bard"],
    },
    {
        "slug": "thunderwave", "name": "Волна грома", "name_en": "Thunderwave", "level": 1,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "На себя (куб 15 футов)",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Волна грома исходит от вас. Каждое существо в кубе 15 футов с центром на вас должно пройти спасбросок Телосложения. При провале существо получает 2d8 урона звуком и отталкивается на 10 футов от вас. При успехе — половина урона без отталкивания. Незакреплённые предметы в области перемещаются.",
        "higher_levels": "Урон возрастает на 1d8 за каждый уровень ячейки выше 1-го.",
        "classes": ["wizard", "druid", "cleric", "bard", "artificer"],
    },
    {
        "slug": "bless", "name": "Благословение", "name_en": "Bless", "level": 1,
        "school": "Enchantment", "casting_time": "1 действие", "spell_range": "30 футов",
        "components": {"v": True, "s": True, "m": "щепотка святой воды"},
        "duration": "Концентрация, до 1 минуты", "concentration": True, "ritual": False,
        "description": "Вы благословляете до трёх существ по вашему выбору в пределах дистанции. Пока заклинание активно, цели добавляют 1d4 к каждому броску атаки и спасброску.",
        "higher_levels": "Ещё одна цель за каждый уровень ячейки выше 1-го.",
        "classes": ["cleric", "paladin"],
    },
    {
        "slug": "detect-magic", "name": "Обнаружение магии", "name_en": "Detect Magic", "level": 1,
        "school": "Divination", "casting_time": "1 действие", "spell_range": "На себя",
        "components": {"v": True, "s": True},
        "duration": "Концентрация, до 10 минут", "concentration": True, "ritual": True,
        "description": "В течение действия заклинания вы чувствуете присутствие магии в радиусе 30 футов. Если вы чувствуете магию таким образом, то можете использовать действие, чтобы увидеть тусклую ауру вокруг видимого волшебного существа или предмета, а также узнать школу магии, если таковая имеется.",
        "classes": ["wizard", "sorcerer", "cleric", "druid", "paladin", "ranger", "bard", "artificer"],
    },
    {
        "slug": "mage-armor", "name": "Доспехи мага", "name_en": "Mage Armor", "level": 1,
        "school": "Abjuration", "casting_time": "1 действие", "spell_range": "Касание",
        "components": {"v": True, "s": True, "m": "кусок выдубленной кожи"},
        "duration": "8 часов", "concentration": False, "ritual": False,
        "description": "Вы касаетесь согласного существа, которое не носит доспехов, и вокруг него возникает защитная магическая сила. КБ цели становится равным 13 + модификатор Ловкости. Заклинание заканчивается, если цель надевает доспехи или вы заканчиваете его.",
        "classes": ["wizard", "sorcerer"],
    },
    {
        "slug": "hex", "name": "Сглаз", "name_en": "Hex", "level": 1,
        "school": "Enchantment", "casting_time": "1 бонусное действие", "spell_range": "90 футов",
        "components": {"v": True, "s": True, "m": "засохший глаз тритона"},
        "duration": "Концентрация, до 1 часа", "concentration": True, "ritual": False,
        "description": "Вы насылаете проклятие на существо в пределах дистанции. Пока заклинание активно, вы наносите цели дополнительно 1d6 урона некротикой каждый раз, когда попадаете по ней атакой. Также выберите одну характеристику при накладывании. Цель совершает проверки этой характеристики с помехой.",
        "higher_levels": "Ячейка 3-4 уровня — 8 часов. Ячейка 5-9 уровня — 24 часа.",
        "classes": ["warlock"],
    },
    {
        "slug": "hunters-mark", "name": "Метка охотника", "name_en": "Hunter's Mark", "level": 1,
        "school": "Divination", "casting_time": "1 бонусное действие", "spell_range": "90 футов",
        "components": {"v": True},
        "duration": "Концентрация, до 1 часа", "concentration": True, "ritual": False,
        "description": "Вы выбираете существо в пределах дистанции как цель охоты. Пока заклинание активно, вы наносите дополнительно 1d6 урона цели каждый раз, когда попадаете по ней атакой оружием. Также у вас есть преимущество на проверки Восприятия и Выживания для нахождения этой цели. Если цель упадёт до 0 хитов, вы можете бонусным действием перенести метку на другое существо.",
        "classes": ["ranger"],
    },
    {
        "slug": "charm-person", "name": "Очарование личности", "name_en": "Charm Person", "level": 1,
        "school": "Enchantment", "casting_time": "1 действие", "spell_range": "30 футов",
        "components": {"v": True, "s": True},
        "duration": "1 час", "concentration": False, "ritual": False,
        "description": "Вы пытаетесь очаровать гуманоида в пределах дистанции. Цель должна пройти спасбросок Мудрости, иначе она будет очарована вами на время действия заклинания. Очарованное существо считает вас добрым знакомым. Заклинание заканчивается досрочно, если вы или ваши спутники атакуете цель.",
        "higher_levels": "Ещё одна цель за каждый уровень ячейки выше 1-го.",
        "classes": ["wizard", "sorcerer", "warlock", "druid", "bard"],
    },
    {
        "slug": "identify", "name": "Опознание", "name_en": "Identify", "level": 1,
        "school": "Divination", "casting_time": "1 минута", "spell_range": "Касание",
        "components": {"v": True, "s": True, "m": "жемчужина стоимостью не менее 100 зм и перо совы"},
        "duration": "Мгновенная", "concentration": False, "ritual": True,
        "description": "Вы выбираете предмет, которого касаетесь. Вы узнаёте все свойства предмета и способ их использования, а также то, зарядился ли он снова, и сколько у него зарядов. Вы также узнаёте, является ли на предмете активным какое-либо заклинание, и что это за заклинание.",
        "classes": ["wizard", "bard", "artificer"],
    },
    # ───────────── 2-й УРОВЕНЬ ─────────────
    {
        "slug": "misty-step", "name": "Туманный шаг", "name_en": "Misty Step", "level": 2,
        "school": "Conjuration", "casting_time": "1 бонусное действие", "spell_range": "На себя",
        "components": {"v": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "На мгновение окутавшись серебристым туманом, вы телепортируетесь на расстояние до 30 футов в незанятое пространство, которое вы видите.",
        "classes": ["wizard", "sorcerer", "warlock", "paladin"],
    },
    {
        "slug": "hold-person", "name": "Удержание личности", "name_en": "Hold Person", "level": 2,
        "school": "Enchantment", "casting_time": "1 действие", "spell_range": "60 футов",
        "components": {"v": True, "s": True, "m": "маленькая прямая железная полоска"},
        "duration": "Концентрация, до 1 минуты", "concentration": True, "ritual": False,
        "description": "Выберите гуманоида, которого вы видите в пределах дистанции. Цель должна пройти спасбросок Мудрости, иначе она будет обездвижена на время действия заклинания. В конце каждого своего хода цель может делать новый спасбросок.",
        "higher_levels": "Ещё одна цель за каждый уровень ячейки выше 2-го.",
        "classes": ["wizard", "sorcerer", "warlock", "cleric", "druid", "bard", "paladin"],
    },
    {
        "slug": "spiritual-weapon", "name": "Духовное оружие", "name_en": "Spiritual Weapon", "level": 2,
        "school": "Evocation", "casting_time": "1 бонусное действие", "spell_range": "60 футов",
        "components": {"v": True, "s": True},
        "duration": "1 минута", "concentration": False, "ritual": False,
        "description": "Вы создаёте парящее призрачное оружие в пределах дистанции. Когда вы накладываете это заклинание, вы можете атаковать этим оружием. Бонусным действием вы можете переместить оружие до 20 футов и атаковать. Урон 1d8 + модификатор заклинательной характеристики.",
        "higher_levels": "Урон возрастает на 1d8 за каждые 2 уровня ячейки выше 2-го.",
        "classes": ["cleric"],
    },
    {
        "slug": "invisibility", "name": "Невидимость", "name_en": "Invisibility", "level": 2,
        "school": "Illusion", "casting_time": "1 действие", "spell_range": "Касание",
        "components": {"v": True, "s": True, "m": "ресница, завёрнутая в смолу из камеди"},
        "duration": "Концентрация, до 1 часа", "concentration": True, "ritual": False,
        "description": "Существо, которого вы касаетесь, становится невидимым до тех пор, пока действует заклинание. Всё, что цель несёт и носит, тоже становится невидимым, пока его несёт цель. Заклинание заканчивается, если цель атакует или накладывает заклинание.",
        "higher_levels": "Ещё одна цель за каждый уровень ячейки выше 2-го.",
        "classes": ["wizard", "sorcerer", "warlock", "bard", "artificer"],
    },
    {
        "slug": "shatter", "name": "Дребезги", "name_en": "Shatter", "level": 2,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "60 футов",
        "components": {"v": True, "s": True, "m": "осколок слюды"},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Внезапный громкий звон в точке в пределах дистанции. Каждое существо в сфере радиусом 10 футов должно пройти спасбросок Телосложения. При провале — 3d8 звукового урона, при успехе — половина. Существа из неорганической материи совершают спасбросок с помехой.",
        "higher_levels": "Урон возрастает на 1d8 за каждый уровень ячейки выше 2-го.",
        "classes": ["wizard", "sorcerer", "warlock", "bard", "artificer"],
    },
    # ───────────── 3-й УРОВЕНЬ ─────────────
    {
        "slug": "fireball", "name": "Огненный шар", "name_en": "Fireball", "level": 3,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "150 футов",
        "components": {"v": True, "s": True, "m": "крошечный шарик из летучей мыши из гуано и серы"},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Яркий луч вырывается из вашего пальца в точку, которую вы выбираете в пределах дистанции, и затем расцветает в беззвучную вспышку пламени. Каждое существо в сфере радиусом 20 футов с центром в этой точке должно пройти спасбросок Ловкости. При провале существо получает урон огнём 8d6, или половину при успехе. Огонь огибает углы. Он поджигает горючие предметы в области.",
        "higher_levels": "Урон возрастает на 1d6 за каждый уровень ячейки выше 3-го.",
        "classes": ["wizard", "sorcerer"],
    },
    {
        "slug": "lightning-bolt", "name": "Молния", "name_en": "Lightning Bolt", "level": 3,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "На себя (линия 100 футов)",
        "components": {"v": True, "s": True, "m": "кусочек меха и стержень из янтаря, стекла или кристалла"},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Разряд молнии вырывается из вас в направлении, которое вы выбираете, в виде линии 100 футов шириной 5 футов. Каждое существо в этой линии должно пройти спасбросок Ловкости. При провале существо получает урон электричеством 8d6, или половину при успехе.",
        "higher_levels": "Урон возрастает на 1d6 за каждый уровень ячейки выше 3-го.",
        "classes": ["wizard", "sorcerer"],
    },
    {
        "slug": "counterspell", "name": "Рассеивание магии", "name_en": "Counterspell", "level": 3,
        "school": "Abjuration", "casting_time": "1 реакция (когда существо в 60 футах накладывает заклинание)",
        "spell_range": "60 футов",
        "components": {"s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Вы пытаетесь прервать накладывание заклинания. Если существо накладывает заклинание 3-го уровня или ниже, оно не срабатывает. Если заклинание 4-го уровня или выше, совершите проверку характеристики. КС равен 10 + уровень заклинания. При успехе — заклинание не срабатывает.",
        "higher_levels": "При использовании ячейки 4-го уровня или выше автоматически нейтрализует заклинание, уровень которого не выше уровня использованной ячейки.",
        "classes": ["wizard", "sorcerer", "warlock"],
    },
    {
        "slug": "revivify", "name": "Оживление", "name_en": "Revivify", "level": 3,
        "school": "Necromancy", "casting_time": "1 действие", "spell_range": "Касание",
        "components": {"v": True, "s": True, "m": "бриллианты на сумму 300 зм, расходуемые заклинанием"},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Вы касаетесь существа, умершего не более 1 минуты назад. Это существо возвращается к жизни с 1 хитом. Это заклинание не может оживить существо, умершее от старости, или не имеющее тела.",
        "classes": ["cleric", "druid", "paladin", "artificer"],
    },
    {
        "slug": "hypnotic-pattern", "name": "Гипнотический узор", "name_en": "Hypnotic Pattern", "level": 3,
        "school": "Illusion", "casting_time": "1 действие", "spell_range": "120 футов",
        "components": {"s": True, "m": "светящаяся палочка или кусочек мерцающей слюды"},
        "duration": "Концентрация, до 1 минуты", "concentration": True, "ritual": False,
        "description": "Вы создаёте крутящийся узор цветов в кубе 30 футов. Каждое существо в области должно пройти спасбросок Мудрости. При провале — очаровано на время действия заклинания (обездвижено и недееспособно). Заклинание прерывается, если очарованное существо получает урон или кто-то его трясёт.",
        "classes": ["wizard", "sorcerer", "warlock", "bard"],
    },
    {
        "slug": "dispel-magic", "name": "Рассеивание магии", "name_en": "Dispel Magic", "level": 3,
        "school": "Abjuration", "casting_time": "1 действие", "spell_range": "120 футов",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Выберите одно существо, предмет или магический эффект в пределах дистанции. Все заклинания 3-го уровня или ниже на цели заканчиваются. Для каждого заклинания 4-го уровня или выше совершите проверку характеристики. КС равен 10 + уровень заклинания.",
        "higher_levels": "При использовании ячейки 4-го уровня или выше автоматически заканчиваются заклинания уровня не выше использованной ячейки.",
        "classes": ["wizard", "sorcerer", "warlock", "cleric", "druid", "bard", "paladin", "ranger"],
    },
    # ───────────── 4-й УРОВЕНЬ ─────────────
    {
        "slug": "banishment", "name": "Изгнание", "name_en": "Banishment", "level": 4,
        "school": "Abjuration", "casting_time": "1 действие", "spell_range": "60 футов",
        "components": {"v": True, "s": True, "m": "предмет, отвратительный цели"},
        "duration": "Концентрация, до 1 минуты", "concentration": True, "ritual": False,
        "description": "Вы пытаетесь отправить одно существо в другое место. Цель должна пройти спасбросок Харизмы. При провале цель перемещается в безвредное дополнительное пространство, пока заклинание активно. Если цель — родная планарная, при успехе она уходит обратно в свой план навсегда.",
        "higher_levels": "Ещё одна цель за каждый уровень ячейки выше 4-го.",
        "classes": ["wizard", "sorcerer", "warlock", "cleric", "paladin"],
    },
    {
        "slug": "greater-invisibility", "name": "Усиленная невидимость", "name_en": "Greater Invisibility", "level": 4,
        "school": "Illusion", "casting_time": "1 действие", "spell_range": "Касание",
        "components": {"v": True, "s": True},
        "duration": "Концентрация, до 1 минуты", "concentration": True, "ritual": False,
        "description": "Вы или существо, которого вы касаетесь, становитесь невидимыми до тех пор, пока активно заклинание. Всё несомое и носимое становится невидимым вместе с ним. В отличие от невидимости, это заклинание не прерывается от атак или накладывания заклинаний.",
        "classes": ["wizard", "sorcerer", "bard"],
    },
    # ───────────── 5-й УРОВЕНЬ ─────────────
    {
        "slug": "hold-monster", "name": "Удержание чудовища", "name_en": "Hold Monster", "level": 5,
        "school": "Enchantment", "casting_time": "1 действие", "spell_range": "90 футов",
        "components": {"v": True, "s": True, "m": "небольшой кусок прямого железного прута"},
        "duration": "Концентрация, до 1 минуты", "concentration": True, "ritual": False,
        "description": "Выберите существо, которое вы видите в пределах дистанции. Цель должна пройти спасбросок Мудрости, иначе будет обездвижена на время действия заклинания. Работает на всех существ, не только гуманоидов. В конце каждого своего хода цель может делать новый спасбросок.",
        "higher_levels": "Ещё одна цель за каждый уровень ячейки выше 5-го.",
        "classes": ["wizard", "sorcerer", "warlock", "bard"],
    },
    {
        "slug": "mass-cure-wounds", "name": "Массовое лечение ран", "name_en": "Mass Cure Wounds", "level": 5,
        "school": "Evocation", "casting_time": "1 действие", "spell_range": "60 футов",
        "components": {"v": True, "s": True},
        "duration": "Мгновенная", "concentration": False, "ritual": False,
        "description": "Волна целительной энергии распространяется из точки в пределах дистанции. Выберите до 6 существ в сфере радиусом 30 футов с центром в этой точке. Каждая цель восстанавливает хиты в количестве 3d8 + ваш модификатор заклинательной характеристики.",
        "higher_levels": "Исцеление возрастает на 1d8 за каждый уровень ячейки выше 5-го.",
        "classes": ["cleric", "druid", "bard"],
    },
    {
        "slug": "teleportation-circle", "name": "Телепортационный круг", "name_en": "Teleportation Circle", "level": 5,
        "school": "Conjuration", "casting_time": "1 минута", "spell_range": "10 футов",
        "components": {"v": True, "m": "мел, чернила и рубин ценой 50 зм (расходуются)"},
        "duration": "1 раунд", "concentration": False, "ritual": False,
        "description": "Вы чертите на земле круг из сигил 10 футов в диаметре, создавая портал, связывающий вас с постоянным кругом телепортации в пределах той же плоскости. Любое существо, попавшее в круг, мгновенно телепортируется в ближайшее свободное пространство у принимающего круга.",
        "classes": ["wizard", "sorcerer", "bard"],
    },
]


def seed_spells(db):
    existing = db.query(Spell).count()
    if existing > 0:
        print(f"  Заклинания уже заполнены ({existing} записей), пропускаем.")
        return

    for spell_data in SPELLS:
        spell = Spell(**spell_data)
        db.add(spell)

    db.commit()
    print(f"  Добавлено заклинаний: {len(SPELLS)}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Заполнение таблицы заклинаний...")
        seed_spells(db)
        print("Готово!")
    finally:
        db.close()
