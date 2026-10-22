# Gemini ilovasi uchun 100 ta so'rov

Bot shu rasmlardan foydalanadi: har bir kadrda qizlarning pozasi va fon gapga qarab almashadi.

## Qanday ishlash kerak
1. **Qahramonlar (64 ta):** Gemini'da yangi suhbat oching va tasdiqlangan **Shohista** rasmini yuklang. Avval **«Boshlash»** so'rovini yozing, keyin pozalarni bittadan yozing. Claire uchun ham alohida suhbat ochib, xuddi shunday qiling.
2. **«_b» variantlari:** shu pozaning o'zi, faqat qo'li boshqa joyda va og'zi ochiq bo'ladi. Bot ikkalasini almashtirib, qo'l va og'iz qimirlayotgandek ko'rsatadi. Har bir pozadan **darhol keyin** uning _b variantini so'rang.
3. **Fonlar (36 ta):** yangi suhbat oching va **«Fon uslubi»** so'rovini yozing. Keyin har bir fonni bittadan so'rang.
4. **Saqlash:** har bir rasmni jadvaldagi **fayl nomi** bilan saqlang.
5. **Yuklash:** GitHub'da **Add file → Upload files** ni bosing.
   - Qahramonlar `assets/raw/` papkasiga, masalan `assets/raw/shohista_laugh.png`.
   - Fonlar `assets/backgrounds/` papkasiga, masalan `assets/backgrounds/cafe.png`.
   - Yoki hammasini shu chatga tashlang, nomlab joylashtirishni o'zim qilaman.
6. Yuklab bo'lgach, **Actions → Run workflow → slot: characters** ni ishga tushiring. Bot yashil fonni kesib, stikerlarni tayyorlaydi.

Bir kunda hammasini qilish shart emas. Avval har qiz uchun 5–6 ta poza va 10 ta fon bo'lsa ham bot ancha jonlanadi.

## Shohista: pozalar

**Boshlash** (rasm bilan birga yuboring):
```
This is Shohista, my cartoon character. In this chat always draw exactly this same character: same face, hair, body shape, clothes and art style, full body from head to shoes, thick white sticker outline, plain solid pure green (#00FF00) background, nothing else, no text, vertical 9:16. Reply only with the image.
```

| # | Fayl nomi | Ma'nosi | So'rov |
|---|---|---|---|
| 1 | `shohista_talk.png` ✅ tayyor | gapiryapti | `New pose: talking happily, one hand gesturing openly.` |
| 2 | `shohista_talk_b.png` | gapiryapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 3 | `shohista_listen.png` | tinglayapti | `New pose: listening attentively with a warm smile, hands together.` |
| 4 | `shohista_listen_b.png` | tinglayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 5 | `shohista_point_up.png` | barmog'ini ko'tarib tushuntiryapti | `New pose: explaining, index finger raised like a teacher.` |
| 6 | `shohista_point_up_b.png` | barmog'ini ko'tarib tushuntiryapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 7 | `shohista_point_side.png` | yonga ko'rsatyapti | `New pose: pointing to the side at something with an open hand.` |
| 8 | `shohista_point_side_b.png` | yonga ko'rsatyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 9 | `shohista_laugh.png` | kulyapti | `New pose: laughing joyfully, eyes squinted, hand near mouth.` |
| 10 | `shohista_laugh_b.png` | kulyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 11 | `shohista_surprised.png` | hayron | `New pose: surprised, eyes wide open, both hands raised.` |
| 12 | `shohista_surprised_b.png` | hayron (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 13 | `shohista_think.png` | o'ylayapti | `New pose: thinking, hand on chin, looking up.` |
| 14 | `shohista_think_b.png` | o'ylayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 15 | `shohista_wave.png` | qo'l silkitib salomlashyapti | `New pose: waving hello with a big smile.` |
| 16 | `shohista_wave_b.png` | qo'l silkitib salomlashyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 17 | `shohista_thumbs_up.png` | barmoq ko'tarib maqtayapti | `New pose: giving a thumbs up, proud smile.` |
| 18 | `shohista_thumbs_up_b.png` | barmoq ko'tarib maqtayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 19 | `shohista_shrug.png` | yelka qisyapti | `New pose: shrugging with a confused smile, palms up.` |
| 20 | `shohista_shrug_b.png` | yelka qisyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 21 | `shohista_excited.png` | xursand, ikki mushti tepada | `New pose: very excited, both fists up, cheerful.` |
| 22 | `shohista_excited_b.png` | xursand, ikki mushti tepada (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 23 | `shohista_shy.png` | uyalib jilmayyapti | `New pose: shy smile, hands clasped, head slightly tilted.` |
| 24 | `shohista_shy_b.png` | uyalib jilmayyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 25 | `shohista_cup.png` | qo'lida piyola/qahva | `New pose: holding a cup of tea or coffee with both hands, smiling.` |
| 26 | `shohista_cup_b.png` | qo'lida piyola/qahva (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 27 | `shohista_phone.png` | telefonga qarayapti | `New pose: looking at a smartphone in her hand.` |
| 28 | `shohista_phone_b.png` | telefonga qarayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 29 | `shohista_book.png` | daftar ushlab o'qiyapti | `New pose: holding an open notebook, studying.` |
| 30 | `shohista_book_b.png` | daftar ushlab o'qiyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 31 | `shohista_bag.png` | xarid sumkasi ushlagan | `New pose: holding a shopping bag.` |
| 32 | `shohista_bag_b.png` | xarid sumkasi ushlagan (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |

## Claire: pozalar

**Boshlash** (rasm bilan birga yuboring):
```
This is Claire, my cartoon character. In this chat always draw exactly this same character: same face, hair, body shape, clothes and art style, full body from head to shoes, thick white sticker outline, plain solid pure green (#00FF00) background, nothing else, no text, vertical 9:16. Reply only with the image.
```

| # | Fayl nomi | Ma'nosi | So'rov |
|---|---|---|---|
| 33 | `claire_talk.png` ✅ tayyor | gapiryapti | `New pose: talking happily, one hand gesturing openly.` |
| 34 | `claire_talk_b.png` | gapiryapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 35 | `claire_listen.png` | tinglayapti | `New pose: listening attentively with a warm smile, hands together.` |
| 36 | `claire_listen_b.png` | tinglayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 37 | `claire_point_up.png` | barmog'ini ko'tarib tushuntiryapti | `New pose: explaining, index finger raised like a teacher.` |
| 38 | `claire_point_up_b.png` | barmog'ini ko'tarib tushuntiryapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 39 | `claire_point_side.png` | yonga ko'rsatyapti | `New pose: pointing to the side at something with an open hand.` |
| 40 | `claire_point_side_b.png` | yonga ko'rsatyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 41 | `claire_laugh.png` | kulyapti | `New pose: laughing joyfully, eyes squinted, hand near mouth.` |
| 42 | `claire_laugh_b.png` | kulyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 43 | `claire_surprised.png` | hayron | `New pose: surprised, eyes wide open, both hands raised.` |
| 44 | `claire_surprised_b.png` | hayron (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 45 | `claire_think.png` | o'ylayapti | `New pose: thinking, hand on chin, looking up.` |
| 46 | `claire_think_b.png` | o'ylayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 47 | `claire_wave.png` | qo'l silkitib salomlashyapti | `New pose: waving hello with a big smile.` |
| 48 | `claire_wave_b.png` | qo'l silkitib salomlashyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 49 | `claire_thumbs_up.png` | barmoq ko'tarib maqtayapti | `New pose: giving a thumbs up, proud smile.` |
| 50 | `claire_thumbs_up_b.png` | barmoq ko'tarib maqtayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 51 | `claire_shrug.png` | yelka qisyapti | `New pose: shrugging with a confused smile, palms up.` |
| 52 | `claire_shrug_b.png` | yelka qisyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 53 | `claire_excited.png` | xursand, ikki mushti tepada | `New pose: very excited, both fists up, cheerful.` |
| 54 | `claire_excited_b.png` | xursand, ikki mushti tepada (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 55 | `claire_shy.png` | uyalib jilmayyapti | `New pose: shy smile, hands clasped, head slightly tilted.` |
| 56 | `claire_shy_b.png` | uyalib jilmayyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 57 | `claire_cup.png` | qo'lida piyola/qahva | `New pose: holding a cup of tea or coffee with both hands, smiling.` |
| 58 | `claire_cup_b.png` | qo'lida piyola/qahva (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 59 | `claire_phone.png` | telefonga qarayapti | `New pose: looking at a smartphone in her hand.` |
| 60 | `claire_phone_b.png` | telefonga qarayapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 61 | `claire_book.png` | daftar ushlab o'qiyapti | `New pose: holding an open notebook, studying.` |
| 62 | `claire_book_b.png` | daftar ushlab o'qiyapti (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |
| 63 | `claire_bag.png` | xarid sumkasi ushlagan | `New pose: holding a shopping bag.` |
| 64 | `claire_bag_b.png` | xarid sumkasi ushlagan (qo'l/og'iz boshqa) | `Same pose as the previous image, but the gesturing hand is in a slightly different position and the mouth is open as if speaking.` |

## Fonlar

**Fon uslubi** (birinchi xabar):
```
In this chat draw backgrounds in one consistent style: Hand-drawn cartoon illustration with bold ink outlines and warm watercolor shading, warm golden light, cozy and detailed. Vertical 9:16 background for a cartoon video. NO people, no characters, no text. Keep the lower half as open floor space and the top third calm and simple. Reply only with the image. First one:
```

| # | Fayl nomi | So'rov |
|---|---|---|
| 65 | `uy_mehmonxona.png` | `Next background: cozy Uzbek home living room with suzani on the wall, low table with tea set, cushions, warm lamp.` |
| 66 | `uy_oshxona.png` | `Next background: Uzbek home kitchen with a big kazan, blue-and-white ceramics on shelves, fruit bowl.` |
| 67 | `choyxona.png` | `Next background: traditional Uzbek choyxona with a wooden tapchan, carpets, teapots and lagan with plov.` |
| 68 | `bozor.png` | `Next background: busy Uzbek bazaar with fruit and vegetable stalls, dried fruits, colorful awnings.` |
| 69 | `registon.png` | `Next background: Registan square in Samarkand with blue-tiled madrasas at golden hour.` |
| 70 | `cafe.png` | `Next background: inside a cozy Parisian café, wooden counter, coffee machine, chalkboard menu, warm lamps.` |
| 71 | `terrace.png` | `Next background: Parisian café terrace with round tables and wicker chairs, the Eiffel Tower in the background.` |
| 72 | `pastry.png` | `Next background: French bakery with a glass display full of croissants, baguettes and macarons.` |
| 73 | `register.png` | `Next background: café cash register counter with a card terminal and a tip jar.` |
| 74 | `restoran.png` | `Next background: elegant French restaurant interior with set tables, candles and wine glasses.` |
| 75 | `metro.png` | `Next background: Paris metro station platform with the classic tiled walls and a metro sign.` |
| 76 | `vokzal.png` | `Next background: grand Paris train station hall with departure boards and platforms.` |
| 77 | `aeroport.png` | `Next background: bright airport terminal with check-in counters and big windows with planes.` |
| 78 | `mehmonxona.png` | `Next background: small hotel reception desk with keys, a bell and a lobby sofa.` |
| 79 | `supermarket.png` | `Next background: French supermarket aisle with shelves of cheese, bread and fruit.` |
| 80 | `dorixona.png` | `Next background: pharmacy interior with a green cross sign, shelves of medicine boxes.` |
| 81 | `shifokor.png` | `Next background: doctor's office with a desk, examination bed and medical posters.` |
| 82 | `sinf.png` | `Next background: language classroom with a blackboard showing French and Uzbek flags, desks.` |
| 83 | `kutubxona.png` | `Next background: cozy library with tall bookshelves and reading lamps.` |
| 84 | `park.png` | `Next background: Paris park (Luxembourg garden) with green chairs, fountain and flower beds.` |
| 85 | `kocha.png` | `Next background: charming Parisian street with shops, flower boxes and street lamps.` |
| 86 | `kiyim_dokoni.png` | `Next background: clothing boutique with racks of dresses, mirrors and a fitting room.` |
| 87 | `pochta.png` | `Next background: post office counter with envelopes, parcels and a scale.` |
| 88 | `bank.png` | `Next background: bank interior with a teller window and an ATM.` |
| 89 | `taksi.png` | `Next background: Paris street at the curb with a yellow taxi stand sign and a waiting car.` |
| 90 | `dengiz.png` | `Next background: sunny French Riviera beach promenade with sea, umbrellas and palm trees.` |
| 91 | `muzey.png` | `Next background: art museum gallery (Louvre-like) with framed paintings and a glass pyramid seen through the window.` |
| 92 | `sena.png` | `Next background: Seine riverside with bookseller stalls, bridges and Notre-Dame in the distance.` |
| 93 | `monmartr.png` | `Next background: Montmartre steps with street lamps and Sacré-Cœur on the hill.` |
| 94 | `oshxona_pishirish.png` | `Next background: kitchen counter ready for cooking with vegetables, pots and a recipe book.` |
| 95 | `yotoqxona.png` | `Next background: bright bedroom in the morning with an alarm clock, bed and a window with sunrise.` |
| 96 | `tugilgan_kun.png` | `Next background: living room decorated for a birthday party with balloons, cake and gifts.` |
| 97 | `toy.png` | `Next background: Uzbek wedding hall with festive decorations, lights and a long table with dishes.` |
| 98 | `avtobus.png` | `Next background: city bus stop with a timetable board and a bench.` |
| 99 | `ish_stoli.png` | `Next background: home desk with a laptop, notebook, coffee cup and a world map on the wall.` |
| 100 | `qor.png` | `Next background: snowy winter street with Christmas lights and a market stall with hot drinks.` |

Jami: **100 ta** so'rov.
