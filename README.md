# 🇫🇷🇺🇿 Uzbekcha_Fransuzcha — avtomatik post boti

Rubrika: **«Fransuzchani o'zbekchada gapirgandek gapiring»**.
Fransuz qiz (Claire) fransuzcha gapiradi, Shohista uni o'qilishi va ma'nosi bilan o'rgatadi.

| Vaqt  | Post                    |
|-------|-------------------------|
| 09:00 | Matnli dars + audio     |
| 14:00 | Rasmli post             |
| 18:00 | Qisqa video (subtitrli) |

Har bir postdan **10 daqiqa oldin** bot sizga postni ko'rsatadi.
- Hech narsa bosmasangiz, post o'z vaqtida chiqadi.
- **✏️ Tahrirlash** ni bossangiz, nimani o'zgartirishni yozasiz. Bot tuzatadi va qayta so'ramasdan chiqaradi.

## 6 agent

1. **Maqolachi** (`researcher.py`): internetdan izlab, dars-dialog yozadi.
2. **Videochi** (`video.py`): rasm, ovoz va subtitrdan vertikal video yasaydi.
3. **Rassom** (`artist.py`): Gemini (Nano Banana) orqali rasm chizadi. Ishlamasa bepul Pollinations, u ham ishlamasa o'zi karta chizadi.
4. **Ovoz** (`voice.py`): bepul Microsoft Edge ovozlari (o'zbekcha Madina, fransuzcha Denise). ElevenLabs kaliti berilsa, o'shani ishlatadi.
5. **Muharrir** (`quality.py`): fransuzcha, talaffuz va imloni tekshiradi.
6. **Nashrchi** (`publisher.py`): sizga ko'rsatadi va kanalga chiqaradi.

---

## O'rnatish (bir marta)

### 1. Fayllarni GitHub'ga yuklash
1. github.com/new manziliga kiring. Nomi: `fransuz-kanal-bot`, **Public** ni tanlang, **Create repository** ni bosing.
   Nega Public? Private repository'da GitHub oyiga 2000 daqiqa bepul beradi, bot esa oyiga taxminan 2500–3000 daqiqa ishlaydi. Public'da cheklov yo'q. Kalitlar baribir Secrets'da yashirin qoladi, kodda hech qanday maxfiy narsa yo'q.
2. Ochilgan sahifada **uploading an existing file** havolasini bosing.
3. Arxivdan chiqargan fayl va papkalarni sudrab tashlang, keyin **Commit changes** ni bosing.

⚠️ `.github` papkasi kompyuterda yashirin bo'lishi mumkin. Yuklangandan keyin repository'da `.github/workflows/post.yml` borligini tekshiring. Agar yo'q bo'lsa:
**Add file → Create new file** ni bosing, nomiga `.github/workflows/post.yml` deb yozing, `post.yml` ichidagi matnni nusxalab qo'ying va saqlang.

### 2. Maxfiy kalitlar (Secrets)
**Settings → Secrets and variables → Actions → Secrets** tabida **New repository secret** tugmasi bilan har birini alohida qo'shing:

| Nomi                 | Qayerdan olinadi                                                    |
|----------------------|---------------------------------------------------------------------|
| `BOT_TOKEN`          | @BotFather → `/newbot` (yoki `/token`). `TELEGRAM_BOT_TOKEN` nomi ham bo'ladi |
| `ADMIN_CHAT_ID`      | @userinfobot ga yozing, u sizga **Id** raqamini beradi              |
| `GEMINI_API_KEY`     | aistudio.google.com/apikey → **Create API key**                     |
| `ELEVENLABS_API_KEY` | *Ixtiyoriy.* elevenlabs.io → profil → **API Keys**. Bo'lmasa bepul ovoz ishlaydi |

🔒 Kalitlarni hech qachon chatga, xabarga yoki kod ichiga yozmang.

### 3. Ochiq sozlamalar (Variables)
O'sha sahifada **Variables** tabini oching va **New repository variable** bilan qo'shing:

| Nomi             | Qiymati                                       |
|------------------|-----------------------------------------------|
| `CHANNEL_ID`     | `@Uzbekcha_Fransuzcha`                        |
| `VOICE_SHOHISTA` | *Ixtiyoriy.* ElevenLabs'dagi o'zbekcha ovoz Voice ID |
| `VOICE_CLAIRE`   | *Ixtiyoriy.* ElevenLabs'dagi fransuzcha ovoz Voice ID|

### 4. Telegram
1. Botni kanalingizga **admin** qilib qo'shing va **xabar joylash** huquqini bering.
2. Botga o'zingiz `/start` deb yozing, aks holda u sizga ogohlantirish yubora olmaydi.

### 5. Birinchi sinov
1. Repository'da **Actions** tabini oching. Agar so'rasa, **I understand… enable** tugmasini bosing.
2. Chapdan **Kanalga avtomatik post** ni tanlang, keyin **Run workflow** ni bosing.
3. `slot` ni tanlang, **test** belgisini qoldiring va **Run workflow** ni bosing.
4. Bir necha daqiqadan keyin bot sizga postni yuboradi. Sinov rejimida u **kanalga chiqmaydi**.

Uchala turini (morning, noon, evening) shunday sinab ko'ring. Hammasi yaxshi bo'lsa, bot jadval bo'yicha o'zi ishlay boshlaydi.

---

## Foydali bilish

- **Qahramonlar bir xil ko'rinishi uchun:** yoqqan rasmlardan 1–3 tasini `assets/` papkasiga yuklang (png yoki jpg). Rassom ularni namuna sifatida oladi.
- **Mavzular takrorlanmaydi:** chiqqan mavzular `data/history.json` ga yoziladi.
- **Xatolik bo'lsa,** bot sizga «❌ Xatolik» deb yozadi. To'liq matni `data/last_error.txt` faylida saqlanadi.
- **Gemini modeli** kalitingizga ochiq modellar ichidan avtomatik tanlanadi. Bepul (billingsiz) kalit ham ishlaydi.
- **GitHub jadvali** ba'zan bir necha daqiqa kechikadi. Shuning uchun ish 30 daqiqa oldin boshlanadi.
- **Jadval to'xtab qolmasligi uchun:** GitHub uzoq vaqt o'zgarishsiz turgan public repository'da jadvalni o'chirib qo'yishi mumkin. Bot har kuni mavzular tarixini yozib turgani uchun bu odatda bo'lmaydi. Agar to'xtasa, **Actions** tabida **Enable workflow** ni bosing.
- **Model nomlari** o'zgarsa, Variables'ga `GEMINI_TEXT_MODEL`, `GEMINI_IMAGE_MODEL` yoki `ELEVEN_MODEL` qo'shib, yangisini yozing.
