"""Obunachi ko'paytirish: jalb qiluvchi birinchi qator, almashinib turuvchi chaqiruvlar, jonli maqsad."""
import datetime

import config

HOOKS = [
    "🤔 Buni fransuzcha ayta olasizmi?",
    "⚡️ 10 soniyada bitta yangi ibora!",
    "🎯 Fransiyada har kuni eshitiladigan ibora:",
    "😎 Bugun shuni o'rganing — do'stlaringizni hayratda qoldiring!",
    "🇫🇷 Fransuz bilan gaplashmoqchimisiz? Shu iboradan boshlang!",
    "👀 Bu iborani bilganlar — fransuzchani tez o'rganadi!",
    "🔥 Eng kerakli iboralardan biri — eslab qoling!",
]

CTAS = [
    "📤 Fransuz tilini o'rganmoqchi bo'lgan do'stingizga yuboring!",
    "🔥 Foydali bo'lsa — reaksiya bosing, bu bizga katta motivatsiya!",
    "👥 Do'stingiz bilan birga o'rganing — postni ulashing!",
    "🔔 Bildirishnomani yoqing — seriyaning davomini o'tkazib yubormang!",
    "📌 Saqlab qo'ying va do'stingizga ham yuboring!",
    "💪 Har kuni 5 daqiqa — va bir yildan keyin fransuzcha gaplashasiz. Do'stingizni ham taklif qiling!",
]

GOALS = [100, 250, 500, 1000, 2000, 3000, 5000, 10000, 20000, 50000, 100000]


def _index(salt=0):
    now = datetime.datetime.now(config.TZ)
    return now.timetuple().tm_yday * 3 + now.hour // 6 + salt


def hook(salt=0):
    return HOOKS[_index(salt) % len(HOOKS)]


def cta(salt=0):
    return CTAS[_index(salt) % len(CTAS)]


_members = {}


def goal_line():
    """«🎯 Maqsad: 500 obunachi! Hozir 365 nafarmiz…» — Telegram'dan jonli son. Xato bo'lsa — bo'sh."""
    try:
        if "n" not in _members:
            import publisher
            _members["n"] = int(publisher._api("getChatMemberCount", chat_id=config.CHANNEL_ID))
        n = _members["n"]
        goal = next(g for g in GOALS if g > n)
        return (f"🎯 <b>Maqsad: {goal} obunachi!</b> Hozir {n} nafarmiz — yana {goal - n} kishi qoldi. "
                f"Do'stingizni taklif qiling! 👇")
    except Exception:
        return ""
