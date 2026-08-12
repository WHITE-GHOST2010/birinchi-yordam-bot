// Telegram WebApp Initialization
const tg = window.Telegram ? window.Telegram.WebApp : null;

if (tg) {
    tg.ready();
    tg.expand();
    
    // Set user info
    const user = tg.initDataUnsafe ? tg.initDataUnsafe.user : null;
    if (user) {
        document.getElementById('user-name').innerText = `${user.first_name} ${user.last_name || ''}`.trim();
        if (user.photo_url) {
            document.getElementById('user-avatar').innerHTML = `<img src="${user.photo_url}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// DARK / LIGHT MODE
// ═══════════════════════════════════════════════════════════════════

function initTheme() {
    const saved = localStorage.getItem('theme') || 'light';
    if (saved === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('theme-toggle-btn').textContent = '☀️';
    } else {
        document.body.classList.remove('dark-mode');
        document.getElementById('theme-toggle-btn').textContent = '🌙';
    }
}

document.getElementById('theme-toggle-btn').addEventListener('click', () => {
    const isDark = document.body.classList.toggle('dark-mode');
    document.getElementById('theme-toggle-btn').textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

initTheme();

// ═══════════════════════════════════════════════════════════════════
// DATA SETS
// ═══════════════════════════════════════════════════════════════════

const FIRST_AID_ITEMS = [
    {
        id: "kuyish",
        title: "🔥 Kuyish",
        icon: "fa-fire-burner",
        color: "var(--accent-orange)",
        bgColor: "var(--accent-orange-bg)",
        desc: "Kuyganda to'g'ri birinchi yordam ko'rsatish va sovutish.",
        steps: [
            "Kuygan joyni zudlik bilan 10-15 daqiqa davomida oqib turgan sovuq (lekin muzdek emas) suv ostida tuting.",
            "Kuygan sohaga steril bog'lam yoki toza latta yoping.",
            "Agar kiyim teriga yopishib qolgan bo'lsa, uni majburlab sug'urib olmang! Atrofini kesib oling.",
            "Bemorga ko'proq suyuqlik (suv, choy) ichiring."
        ],
        prohibited: "Kuygan joyga yog', sariyog', tish pastasi yoki spirt surtmang! Hosil bo'lgan pufakchalarni aslo yormang!"
    },
    {
        id: "qon_ketishi",
        title: "🩸 Qon ketishi",
        icon: "fa-droplet",
        color: "var(--accent-red)",
        bgColor: "var(--accent-red-bg)",
        desc: "Kuchli qon ketishini to'xtatish va jgut bog'lash qoidalari.",
        steps: [
            "Yara ustiga toza bog'lam yoki latta qo'yib, qo'l bilan 5-10 daqiqa davomida mahkam bosing.",
            "Iloji bo'lsa, jarohatlangan a'zoni (oyoq yoki qo'l) yurak sathidan balandroq ko'taring.",
            "Kuchli arterial (och qizil, otilib chiquvchi) qon ketishida yaraning yuqori qismidan turniket (jgut) bog'lang va vaqtini yozib qo'ying.",
            "Turniketni yozda 1.5 soat, qishda 1 soatdan ortiq bog'liq qoldirmang. Har 30 daqiqada bo'shatib turing."
        ],
        prohibited: "Yaradagi yot jismlarni (shisha bo'lagi, sim, mix) o'zboshimchalik bilan sug'urib olmang! Bu qon ketishini kuchaytiradi."
    },
    {
        id: "sinish",
        title: "🦴 Suyak sinishi",
        icon: "fa-bone",
        color: "var(--accent-blue)",
        bgColor: "var(--accent-blue-bg)",
        desc: "Suyak singanda shina qo'yish va og'riqsizlantirish.",
        steps: [
            "Shikastlangan a'zoni (qo'l yoki oyoqni) harakatsiz holatga keltiring.",
            "Shina sifatida taxtacha, qattiq karton yoki har qanday tekis buyumdan foydalanib bog'lang (singan bo'g'imning pastki va yuqori qismini qamrab olsin).",
            "Shish va og'riqni kamaytirish uchun latta bilan o'ralgan muz qo'ying.",
            "Ochiq sinishda avval yaraga steril bog'lam qo'ying, so'ngra shinani mahkamlang."
        ],
        prohibited: "Singan suyakni o'z joyiga solishga yoki to'g'rilashga urinmang! Bemorni ortiqcha harakatlantirmang."
    },
    {
        id: "bogilish",
        title: "🫣 Bo'g'ilish",
        icon: "fa-head-side-cough",
        color: "var(--accent-orange)",
        bgColor: "var(--accent-orange-bg)",
        desc: "Tomoqqa narsa tiqilib qolganda Geymlix usulini qo'llash.",
        steps: [
            "Agar bemor yo'tala olsa, uni qattiqroq yo'talishga undang (eng yaxshi tabiiy yo'l).",
            "Bemor ozroq oldinga engashsin. Kaftingiz asosi bilan uning kuraklari orasiga 5 marta kuchli zarb bilan uring.",
            "Geymlix usuli: Bemor orqasidan turib, belidan quchoqlang. Bir qo'lni musht qilib, kindikdan biroz yuqoriga qo'ying. Ikkinchi qo'l bilan mushtni tutib, o'zingizga va yuqoriga qarab 5 marta keskin torting.",
            "Hushsiz holatda: Bemorni tekis yotqizib, zudlik bilan sun'iy nafas va yurak massajini boshlang."
        ],
        prohibited: "Tomoqdagi yot jismni ko'rmasdan turib barmoq bilan qidirib tortishga urinmang! Uni yanada chuqurroq tiqib yuborishingiz mumkin."
    },
    {
        id: "yurak_xuruji",
        title: "💔 Yurak xuruji",
        icon: "fa-heart-circle-xmark",
        color: "var(--accent-red)",
        bgColor: "var(--accent-red-bg)",
        desc: "Ko'krak qafasidagi kuchli siquvchi og'riqda tezkor choralar.",
        steps: [
            "Bemorni zudlik bilan yarim o'tirgan holatga keltiring, tinchlantiring va ortiqcha harakatlarni taqiqlang.",
            "Yoqasini oching, bo'yinbog'ini bo'shating, derazani ochib toza havo kelishini ta'minlang.",
            "Zudlik bilan tez yordam (103) chaqiring.",
            "Bemor hushini yo'qotsa va nafasdan qolsa, kechiktirmasdan yurak-o'pka reanimatsiyasini boshlang."
        ],
        prohibited: "Bemorni turishga, yurishga yoki jismoniy zo'riqishga majburlamang! Bemorni yolg'iz qoldirmang."
    },
    {
        id: "hushdan_ketish",
        title: "😵 Hushdan ketish",
        icon: "fa-face-dizzy",
        color: "var(--accent-blue)",
        bgColor: "var(--accent-blue-bg)",
        desc: "Hushini yo'qotgan odamni o'ziga keltirish va yotqizish.",
        steps: [
            "Bemorni tekis joyga orqasi bilan yotqizib, oyoqlarini 30 sm balandlikka ko'taring (miya qon aylanishini yaxshilash uchun).",
            "Nafas olishini osonlashtirish uchun kiyimlarini bo'shating (tugmalarni yeching).",
            "Noshadir spirtini paxtaga tomizib, burunga 5-10 sm masofadan hidlatib ko'ring.",
            "Agar bemor nafas olayotgan bo'lsa-yu hushiga kelmasa, uni xavfsiz yonbosh holatga yotqizib qo'ying."
        ],
        prohibited: "Hushsiz odamning og'ziga suv quymang yoki dori tiqmang! U tiqilib bo'g'ilib qolishi mumkin."
    },
    {
        id: "zaharlanish",
        title: "🧪 Zaharlanish",
        icon: "fa-flask-poisonous",
        color: "var(--accent-green)",
        bgColor: "var(--accent-green-bg)",
        desc: "Kimyoviy moddalar yoki eskirgan taomdan zaharlanish.",
        steps: [
            "Zahar og'iz orqali kirgan va bemor hushida bo'lsa, tezda 1 litrgacha iliq suv ichirib, tilining ildiziga bosib qustiring.",
            "Zaharni bog'lash uchun faollashtirilgan ko'mir bering (har 10 kg vazn uchun 1 tabletka).",
            "Bemor ko'p suyuqlik ichishi kerak (suvsizlanishni oldini olish uchun).",
            "Zaharli gazdan zaharlanganda zudlik bilan toza havoga olib chiqing va kiyimlarini bo'shating."
        ],
        prohibited: "Kislota, ishqor yoki neft mahsulotlari bilan zaharlanganda qustirish mutlaqo taqiqlanadi (qizilo'ngachni qayta kuydiradi!)."
    },
    {
        id: "issiqlik_urishi",
        title: "☀️ Issiqlik urishi",
        icon: "fa-sun",
        color: "var(--accent-orange)",
        bgColor: "var(--accent-orange-bg)",
        desc: "Quyosh va issiq havoda tana harorati ko'tarilganda sovutish.",
        steps: [
            "Bemorni zudlik bilan soya, salqin va havo aylanadigan joyga olib o'ting.",
            "Ustki kiyimlarini yeching yoki bo'shating.",
            "Peshonasiga, bo'yniga, qo'ltiq ostiga sovuq suvda ho'llangan latta qo'ying.",
            "Hushida bo'lsa, tez-tez oz-ozdan sovuq suv yoki mineral suv ichiring."
        ],
        prohibited: "Tana harorati juda yuqori bo'lganda bemorni muzdek suvli vannaga birdan solmang (shok holatiga tushishi mumkin)."
    }
];

const DISEASES_DATA = [
    { name: "Gripp", cat: "Infeksiya", desc: "O'tkir respirator virusli infeksiya. Yuqori harorat, burun oqishi va bo'g'imlar og'rig'i bilan kechadi.", aid: "Bemorga ko'p iliq suyuqlik ichiring, isitma tushiruvchi dorilar bering, xonani tez-tez shamollating." },
    { name: "SORS (shamollash)", cat: "Infeksiya", desc: "Burun va tomoqning o'tkir shamollashi.", aid: "Dam olish, iliq choy ichish, tomoqni chayish va burunga sho'r suv tomizish." },
    { name: "Angina", cat: "Tomoq", desc: "Tomoq bezlarining o'tkir yallig'lanishi, yutish qiyinligi va yuqori harorat.", aid: "Antiseptik eritmalarda tomoqni chayish, shifokor buyurgan antibiotiklarni qabul qilish." },
    { name: "Bronxit", cat: "Nafas", desc: "Bronxlar shilliq qavatining yallig'lanishi, kuchli yo'tal.", aid: "Ko'p suyuqlik ichish, ingalyatsiya qilish, yo'talga qarshi shifokor yozgan dorilar." },
    { name: "Pnevmoniya", cat: "Nafas", desc: "O'pkaning yallig'lanishi. Qiyin nafas olish va isitma bilan kechadi.", aid: "Zudlik bilan shifokor chaqirish, shifoxonada davolanish tavsiya etiladi." },
    { name: "Astma", cat: "Nafas", desc: "Nafas qisilishi xurujlari bilan kechadigan surunkali kasallik.", aid: "Xuruj paytida bemorni o'tqizib, bronx kengaytiruvchi shaxsiy ingalyatoridan foydalanishga yordam bering." },
    { name: "Sil (tuberkulyoz)", cat: "Infeksiya", desc: "O'pkani shikastlovchi yuqumli bakterial kasallik.", aid: "Zudlik bilan shifokor nazoratida uzoq muddatli maxsus antibiotiklar kursini olish." },
    { name: "COVID-19", cat: "Infeksiya", desc: "Koronavirus keltirib chiqaradigan o'tkir infeksiya.", aid: "Izolyatsiya qilish, tana haroratini nazorat qilish va shifokor ko'rsatmasi bilan davolanish." },
    { name: "Sinusit", cat: "Nafas", desc: "Burun atrofi bo'shliqlarining yallig'lanishi, bosh og'rig'i.", aid: "Burunni tuzli suv bilan yuvish, shifokor buyurgan tomchilar va dori vositalari." },
    { name: "Otit (quloq yallig'lanishi)", cat: "Quloq", desc: "Quloq yo'lining o'tkir yallig'lanishi, kuchli og'riq va isitma.", aid: "Quloqqa issiq narsa bosmaslik, shifokor buyurgan tomchilardan foydalanish, og'riqsizlantirish." },
    { name: "Gastrit", cat: "Oshqozon", desc: "Oshqozon shilliq qavati yallig'lanishi, achishish og'rig'i.", aid: "Parhez qilish (achchiq va yog'lidan tiyilish), me'yorida ovqatlanish, shifokor dorilari." },
    { name: "Oshqozon yarasi", cat: "Oshqozon", desc: "Oshqozon yoki o'n ikki barmoqli ichak devorida yara paydo bo'lishi.", aid: "Qat'iy parhez, kislotalilikni kamaytiruvchi dorilar ichish, shoshilinchda shifokorga murojaat." },
    { name: "Pankreatit", cat: "Oshqozon", desc: "Oshqozon osti bezining yallig'lanishi, kuchli o'rab oluvchi og'riq.", aid: "Ochlik (1-2 kun ovqat yemaslik), sovuq kompres, zudlik bilan shifokor chaqirish." },
    { name: "Xoletsistit", cat: "Oshqozon", desc: "O't pufagining yallig'lanishi, o'ng qovurg'a ostida og'riq.", aid: "Yog'li ovqatlardan voz kechish, spasmolitiklar va shifokor nazoratida davolanish." },
    { name: "Gepatit", cat: "Jigar", desc: "Jigarning virusli yoki toksik yallig'lanishi, sarg'ayish.", aid: "Jismoniy zo'riqishdan qochish, qat'iy parhez, gepatolog shifokor nazorati." },
    { name: "Kolit", cat: "Ichak", desc: "Yo'g'on ichak shilliq qavatining yallig'lanishi, qorin dam bo'lishi.", aid: "Yengil hazm bo'luvchi taomlar, ko'p suyuqlik, shifokor buyurgan fermentlar." },
    { name: "Appenditsit", cat: "Oshqozon", desc: "Ko'richak o'simtasining o'tkir yallig'lanishi, o'ng yonboshdagi kuchli og'riq.", aid: "Hech qanday og'riq qoldiruvchi yoki issiq narsa bosmasdan, tez yordam chaqirish." },
    { name: "Gemorroy", cat: "Ichak", desc: "To'g'ri ichak venalarining kengayishi va tugunlar hosil bo'lishi.", aid: "Faol harakat, toza gigiyena, parhez (kletchatkaga boy taomlar), shamchalar." },
    { name: "Qabziyat (ich qotishi)", cat: "Ichak", desc: "Defekatsiyaning qiyinlashishi yoki kechikishi.", aid: "Ko'p suv ichish, kletchatkaga boy mevalar yeyish, surkash dori vositalari." },
    { name: "Diareya (ich ketishi)", cat: "Ichak", desc: "Tez-tez va suyuq axlat kelishi, suvsizlanish xavfi.", aid: "Regidron eritmasini ichish, adsorbentlar (faollashtirilgan ko'mir) qabul qilish." },
    { name: "Gipertoniya", cat: "Yurak", desc: "Qon bosimining surunkali ravishda yuqoki bo'lishi.", aid: "Tinch holatda o'tirish, shifokor buyurgan bosim tushiruvchi dori qabul qilish." },
    { name: "Gipotoniya", cat: "Yurak", desc: "Qon bosimining me'yordan past bo'lishi, holsizlik.", aid: "Iliq shirin choy yoki qahva ichish, oyoqlarni balandroq ko'tarib yotish." },
    { name: "Aritmiya", cat: "Yurak", desc: "Yurak urish maromining buzilishi (tezlashishi yoki sekinlashishi).", aid: "Tinchlanish, chuqur nafas olish, shifokor buyurgan dori vositalarini ichish." },
    { name: "Ateroskleroz", cat: "Yurak", desc: "Qon tomirlarida xolesterin pilyakalari to'planishi va torayishi.", aid: "Yog'siz parhez, sport bilan shug'ullanish, shifokor nazoratida xolesterinni kamaytirish." },
    { name: "Varikoz", cat: "Yurak", desc: "Oyoq venalarining kengayishi va qon aylanishi buzilishi.", aid: "Uzoq tik turmaslik, maxsus elastik paypoqlar kiyish, oyoqlarni ko'tarib dam olish." },
    { name: "Stenokardiya", cat: "Yurak", desc: "Yurak mushagiga qon yetishmasligi tufayli ko'krakdagi qisqa og'riq.", aid: "Bemorni tinchlantirish, til ostiga nitroglicerin qo'yish, og'riq o'tmasa tez yordam chaqirish." },
    { name: "Insult belgilari", cat: "Miya", desc: "Miyada qon aylanishining to'satdan buzilishi (nutq va harakat yo'qolishi).", aid: "Bemorni yotqizib, boshini biroz ko'tarish, zudlik bilan 103 chaqirish." },
    { name: "Infarkt belgilari", cat: "Yurak", desc: "Yurak mushagi bir qismining qon kelmasligi tufayli nobud bo'lishi.", aid: "Nitroglicerin bering, yoqasini ochib toza havo bering va darhol tez yordam chaqiring!" },
    { name: "Anemiya (kamqonlik)", cat: "Qon", desc: "Qonda gemoglobin va qizil qon tanachalari kamayishi.", aid: "Temir moddasiga boy taomlar yeyish (go'sht, anor), shifokor yozgan temir preparatlari." },
    { name: "Tromboflebit", cat: "Yurak", desc: "Vena tomirlarida tromb hosil bo'lishi va yallig'lanish.", aid: "Jarohatlangan oyoqni harakatsiz saqlash, sovuq kompres, shifokorga murojaat qilish." },
    { name: "Qandli diabet", cat: "Endokrin", desc: "Qonda glyukoza (shakar) miqdorining oshib ketishi.", aid: "Parhez, glyukoza miqdorini muntazam tekshirish va shaxsiy insulindan foydalanish." },
    { name: "Zob (buqoq)", cat: "Endokrin", desc: "Qalqonsimon bezning kattalashishi va yod yetishmasligi.", aid: "Ratsionda yodlangan tuz va dengiz mahsulotlarini ko'paytirish, endokrinolog nazorati." },
    { name: "Semizlik", cat: "Metabolizm", desc: "Tana vaznining yog' hisobiga me'yordan ortiq bo'lishi.", aid: "Kam kaloriyali parhez, muntazam jismoniy mashqlar, shifokor ko'rigi." },
    { name: "Gipotireoz", cat: "Endokrin", desc: "Qalqonsimon bez gormonlarining yetishmasligi, charchoq.", aid: "Endokrinolog shifokor buyurgan gormonal o'rinbosar dorilarni qabul qilish." },
    { name: "Buyrak toshi", cat: "Buyrak", desc: "Buyrak bo'shliqlarida tuz va minerallardan tosh hosil bo'lishi.", aid: "Ko'p suv ichish, spasmolitiklar ichish, kuchli og'riqda shifokorga borish." },
    { name: "Sistit", cat: "Siydik", desc: "Qovuq shilliq qavatining yallig'lanishi, og'riqli siyish.", aid: "Iliq kiyinish, ko'p iliq suyuqlik ichish, urolog buyurgan antibakterial dorilar." },
    { name: "Pielonefrit", cat: "Buyrak", desc: "Buyrak jomining bakterial yallig'lanishi, bel og'rig'i, isitma.", aid: "Issiq saqlanish, zudlik bilan shifokorga murojaat qilish va antibiotik davolash." },
    { name: "Prostatit", cat: "Tanosil", desc: "Prostata bezining yallig'lanishi, siyish qiyinlashishi.", aid: "Sovuq qotishdan saqlanish, urolog shifokor ko'rigidan o'tish va dori olish." },
    { name: "Uretrit", cat: "Siydik", desc: "Siydik yo'lining yallig'lanishi, achishish va og'riq.", aid: "Shaxsiy gigiyena, ko'p suv ichish, shifokor buyurgan antibiotiklar." },
    { name: "Adneksit", cat: "Tanosil", desc: "Ayollarda tuxumdon va bachadon naylarining yallig'lanishi.", aid: "Sovuqdan saqlanish, zudlik bilan ginekolog shifokor ko'rigidan o'tish." },
    { name: "Dermatit", cat: "Teriga", desc: "Teri yallig'lanishi, qizarish, qichishish va toshmalar.", aid: "Allergenlar bilan aloqani uzish, namlantiruvchi kremlar surtish, shifokor malhamlari." },
    { name: "Ekzema", cat: "Teriga", desc: "Terining surunkali allergik yallig'lanishi, qavariqlar.", aid: "Terini quritmaslik, parhez qilish, dermatolog yozgan gormonal malhamlar." },
    { name: "Psoriaz", cat: "Teriga", desc: "Terida kumushsimon tangachalar hosil qiluvchi surunkali kasallik.", aid: "Stressdan qochish, quyosh nuri, terini namlash, shifokor nazoratida davolash." },
    { name: "Allergiya", cat: "Teriga", desc: "Tashqi omillarga terining qizarish va toshma ko'rinishidagi reaksiyasi.", aid: "Antigistamin dori ichish, allergen moddani aniqlab undan uzoq bo'lish." },
    { name: "Eshakemi", cat: "Teriga", desc: "Terida qichishuvchi shishlar paydo bo'lishi (allergik reaksiya).", aid: "Antigistamin dori qabul qilish, sovuq kompres qo'yish, parhez qilish." },
    { name: "Husnbuzar (akne)", cat: "Teriga", desc: "Yog' bezlarining tiqilishi va yallig'lanishi, toshmalar.", aid: "Yuzni toza saqlash, yog'li ovqatlardan cheklanish, kosmetolog/dermatolog tavsiyalari." },
    { name: "Temiratki", cat: "Teriga", desc: "Terining infeksion yoki virusli kasalligi, halqasimon toshmalar.", aid: "Shaxsiy gigiyena buyumlarini ajratish, zudlik bilan dermatologga uchrash." },
    { name: "Gribok", cat: "Teriga", desc: "Teri yoki tirnoqlarning zamburug'li kasalligi.", aid: "Oyoqlarni quruq saqlash, maxsus zamburug'ga qarshi malhamlar surtish." },
    { name: "Qazg'oq", cat: "Teriga", desc: "Bosh terisining quruqlashishi yoki yog'lanishi natijasida tangachalar to'kilishi.", aid: "Maxsus shampunlar ishlatish, shirinliklarni kamaytirish." },
    { name: "Soch to'kilishi", cat: "Teriga", desc: "Sochlarning me'yordan ortiq to'kilishi (alopetsiya).", aid: "Vitaminlar qabul qilish (B guruhi, rux), tricholog shifokor ko'rigi." },
    { name: "Migren", cat: "Asab", desc: "Boshning bir yarmini qoplab oladigan kuchli xurujli og'riq.", aid: "Qorong'i va tinch xonada yotish, og'riq qoldiruvchi dori ichish, boshga sovuq latta qo'yish." },
    { name: "Nevralgiya", cat: "Asab", desc: "Asab tolalari bo'ylab kuchli va to'satdan paydo bo'luvchi og'riq.", aid: "Og'rigan joyni issiq saqlash, tinchlik, shifokor buyurgan vitamin va spasmolitiklar." },
    { name: "Radikulit", cat: "Tayanch", desc: "Orqa miya asab ildizlarining siqilishi va og'rishi.", aid: "Qattiq o'rinda yotish, belni issiq jun ro'mol bilan o'rash, yallig'lanishga qarshi malhamlar." },
    { name: "Osteoxondroz", cat: "Tayanch", desc: "Umarqa disklarining yemirilishi, bel va bo'yindagi og'riq.", aid: "To'g'ri qomatni saqlash, yengil mashqlar qilish, massaj, shifokor ko'rsatmalari." },
    { name: "Artrit", cat: "Tayanch", desc: "Bo'g'imlarning yallig'lanishi, shish va harakat qiyinligi.", aid: "Bo'g'imlarga og'irlik bermaslik, issiq bog'lamlar qilish, shifokor dori vositalari." },
    { name: "Artroz", cat: "Tayanch", desc: "Bo'g'im tog'aylarining surunkali yemirilishi va qotishi.", aid: "Vaznni kamaytirish, mo''tadil jismoniy faollik, shifokor buyurgan xondroprotektorlar." },
    { name: "Podagra", cat: "Tayanch", desc: "Organizmda siydik kislotasi to'planishi tufayli bo'g'imlar og'rig'i.", aid: "Go'sht va dukkakli mahsulotlarni cheklash (parhez), ko'p suv ichish, og'riqsizlantirish." },
    { name: "Skolioz", cat: "Tayanch", desc: "Umarqa pog'onasining yon tomonga qiyshayishi.", aid: "Davolash gimnastikasi bilan shug'ullanish, suzish, ortopedik matrasda yotish." },
    { name: "Oyoq uvishishi", cat: "Asab", desc: "Oyoqlarda qon aylanishi yoki asab o'tkazuvchanligi buzilishi.", aid: "Oyoqlarni uqalash, oyoq kiyimni tekshirish, shifokor ko'rigidan o'tish." },
    { name: "Uyqusizlik", cat: "Asab", desc: "Uxlashga qiynalish yoki uyqu sifatining yomonligi.", aid: "Kechasi telefondan foydalanmaslik, xonani shamollatish, iliq dush va tinchlantiruvchi choylar." },
    { name: "Kon'yunktivit", cat: "Ko'z", desc: "Ko'z shilliq pardasining yallig'lanishi, qizarish va yoshlanish.", aid: "Ko'zni qaynatilgan iliq suv yoki moychechak suvi bilan yuvish, antiseptik tomchilar tomizish." },
    { name: "Katarakta", cat: "Ko'z", desc: "Ko'z gavharining xiralashishi, ko'rish qobiliyati pasayishi.", aid: "Faqat jarrohlik yo'li bilan davolanadi, ko'z shifokori (oftalmolog) ko'rigi shart." },
    { name: "Glaukoma", cat: "Ko'z", desc: "Ko'z ichki bosimining oshishi, ko'rish asabining shikastlanishi.", aid: "Muntazam ravishda ko'z bosimini o'lchash, shifokor buyurgan tomchilarni tomizish." },
    { name: "Arpa (ko'zda)", cat: "Ko'z", desc: "Ko'z qovog'idagi yog' bezining o'tkir yiringli yallig'lanishi.", aid: "Yiringni aslo siqmang! Ko'zni toza tuting, shifokor buyurgan antibiotikli malhamlar surting." },
    { name: "Blefarit", cat: "Ko'z", desc: "Ko'z qovoqlari chetlarining surunkali yallig'lanishi.", aid: "Qovoqlarni maxsus eritmalar bilan tozalash, gigiyena qoidalariga rioya etish." },
    { name: "Karies", cat: "Tish", desc: "Tish qattiq to'qimalarining yemirilishi va bo'shliq hosil bo'lishi.", aid: "Tishlarni kuniga 2 marta yuvish, stomatolog shifokorga borib tishni plombalash." },
    { name: "Stomatit", cat: "Og'iz", desc: "Og'iz shilliq qavatida mayda yaralar paydo bo'lishi, og'riq.", aid: "Og'izni furatsilin yoki moychechak damlamasi bilan chayish, shifokor yozgan gellar." },
    { name: "Gingivit", cat: "Tish", desc: "Milklarning yallig'lanishi va qonashi, og'izdan hid kelishi.", aid: "Yumshoq tish cho'tkasidan foydalanish, og'izni chayish, tish toshlarini tozalash." },
    { name: "Pulpit", cat: "Tish", desc: "Tish ichidagi asab tolasining yallig'lanishi, chidab bo'lmas kuchli og'riq.", aid: "Og'riq qoldiruvchi dori ichish va tezda stomatolog shifokorga murojaat qilish." },
    { name: "Tish og'rig'i", cat: "Tish", desc: "Tish yoki uning atrofidagi to'qimalarda og'riq sezilishi.", aid: "Iliq tuzli suvda og'izni chayish, og'riq qoldiruvchi dori qabul qilish va shifokorga uchrash." },
    { name: "Suvchechak", cat: "Yuqumli", desc: "Isitma va butun tanaga qichishuvchi pufakchalar toshishi bilan kechuvchi virus.", aid: "Toshmalarga ko'k dori (zelenka) surtish, bemorni alohidalash, qichishga qarshi dori ichish." },
    { name: "Qizamiq", cat: "Yuqumli", desc: "Yuqori harorat, yo'tal va butun tanaga toshma toshishi.", aid: "Bemorni alohidalash, ko'p suyuqlik ichirish, qorong'iroq xonada saqlash (ko'zlarni himoyalash)." },
    { name: "Tepki (parotit)", cat: "Yuqumli", desc: "Quloq oldi so'lak bezlarining yallig'lanishi va shishishi.", aid: "Tomoq va bo'yinni issiq saqlash, yengil chaynaladigan ovqatlar yeyish, shifokor nazorati." },
    { name: "Qizilcha", cat: "Yuqumli", desc: "Mayda pushti toshmalar toshishi va limfa tugunlari kattalashishi.", aid: "Ko'p suyuqlik ichish, dam olish, harorat ko'tarilsa isitma tushiruvchi dorilar berish." },
    { name: "Dizenteriya", cat: "Yuqumli", desc: "Yo'g'on ichakning og'ir shikastlanishi, qonli diareya, isitma.", aid: "Zudlik bilan shifokorga murojaat qilish, ko'p suyuqlik va regidron ichish." },
    { name: "Gelmintoz (gijja)", cat: "Yuqumli", desc: "Gijjalar bilan zararlanish, qorin og'rig'i, ishtahasizlik.", aid: "Shaxsiy gigiyenaga rioya qilish, shifokor tavsiya qilgan gijjaga qarshi dorilarni ichish." },
    { name: "Salmonellyoz", cat: "Yuqumli", desc: "Bakterial ichak infeksiyasi, qusish, diareya va isitma.", aid: "Regidron eritmasini ichish, adsorbentlar qabul qilish, zudlik bilan shoshilinch yordam olish." },
    { name: "Vabo", cat: "Yuqumli", desc: "Kuchli qusish va ich ketishi natijasida suvsizlanish keltiruvchi vabo.", aid: "Zudlik bilan kasalxonaga yotqizish, organizmda tuz va suv balansini tiklash (tuzli eritmalar)." },
    { name: "Kuydirgi", cat: "Yuqumli", desc: "Hayvonlardan yuquvchi xavfli yuqumli kasallik, terida qora yaralar.", aid: "Zudlik bilan infeksionist shifokor nazoratida kasalxonada antibiotik davolash olish." },
    { name: "Quturish", cat: "Yuqumli", desc: "Quturgan hayvonlar tishlaganda yuqadigan o'lim xavfi bor virus.", aid: "Jarohatni zudlik bilan sovunlab yuvish va 1-2 soat ichida shoshilinch vaksina olish!" },
    { name: "Depressiya", cat: "Ruhiy", desc: "Uzoq muddatli tushkunlik, hayotga qiziqish yo'qolishi.", aid: "Yaqinlar bilan suhbatlashish, jismoniy faollik, psixoterapevt shifokor yordami." },
    { name: "Nevroz", cat: "Ruhiy", desc: "Asab tizimining charchashi tufayli yuzaga keladigan asabiylik.", aid: "Ish va dam olish rejimini to'g'rilash, tinchlantiruvchi damlamalar ichish, dam olish." },
    { name: "Vahima xuruji", cat: "Ruhiy", desc: "To'satdan kuchli qo'rquv va yurak tez urishi xuruji.", aid: "Chuqur va sekin nafas oling, o'zingizga xavfsiz joyda ekanligingizni qayta-qayta ayting." },
    { name: "Stress", cat: "Ruhiy", desc: "Tashqi bosimlarga nisbatan organizmning himoya reaksiyasi.", aid: "Chuqur nafas olish mashqlari, meditatsiya, toza havoda yurish, kofeinni kamaytirish." },
    { name: "Surunkali charchash", cat: "Ruhiy", desc: "Uzoq dam olishdan keyin ham o'tib ketmaydigan holsizlik.", aid: "Uyqu rejimini tartibga solish, vitaminlar qabul qilish, dam olish kunlarini tashkil etish." },
    { name: "Asabiylik", cat: "Ruhiy", desc: "Tez ta'sirlanish va his-tuyg'ularni nazorat qila olmaslik.", aid: "Biroz tinchlanish, vaziyatdan uzoqlashish, tinchlantiruvchi o'tli choylar ichish." },
    { name: "Bosh aylanishi", cat: "Umumiy", desc: "Muvozanatni yo'qotish va atrofdagi narsalar aylanayotgandek tuyulishi.", aid: "Bemorni darhol yotqizish yoki o'tqizish, boshini qimirlatmaslik, shirin choy berish." },
    { name: "Quloq bitishi", cat: "Quloq", desc: "Quloq ichida havo bosimi o'zgarishi yoki oltingugurt tiqilishi.", aid: "Yutunish harakatlari qilish, aslo quloqni o'tkir buyumlar bilan kovlamaslik!" },
    { name: "Burun qonashi", cat: "Umumiy", desc: "Burun bo'shlig'i tomirlarining yorilishi va qon ketishi.", aid: "Boshni biroz oldinga engash (orqaga emas!), burun qanotlarini 5-10 daqiqa siqib turish." },
    { name: "Tomoq og'rig'i", cat: "Tomoq", desc: "Tomoq yallig'lanishi tufayli yutish va gapirishda noqulaylik.", aid: "Iliq tuzli suvda tomoqni tez-tez chayish, ko'p iliq choy va suyuqliklar ichish." },
    { name: "Quyosh urishi", cat: "Travma", desc: "Quyosh nurlari ostida uzoq qolib ketish natijasida bosh og'rishi, isitma.", aid: "Bemorni soya va salqin joyga olib o'tish, peshonaga sovuq kompres qo'yish, suv ichirish." },
    { name: "Sovuq urishi", cat: "Travma", desc: "Past harorat ta'sirida tana a'zolarining muzlashi va shikastlanishi.", aid: "Bemorni asta-sekin iliq xonaga olib kirish, iliq choy berish (birdan issiq suvga solmang!)." },
    { name: "Miya chayqalishi", cat: "Travma", desc: "Boshga kuchli zarba tegishi natijasida ko'ngil aynishi, bosh og'rig'i.", aid: "Bemorni tekis yotqizib, boshini biroz ko'tarib qo'ying va zudlik bilan 103 chaqiring." },
    { name: "Lat yeyish", cat: "Travma", desc: "Yumshoq to'qimalarning yopiq shikastlanishi, shish va ko'karish.", aid: "Zararlangan joyga darhol muz qo'yish (latta orqali), shikastlangan a'zoni tinch saqlash." },
    { name: "Pay cho'zilishi", cat: "Travma", desc: "Bo'g'imlardagi paylarning keskin harakat tufayli cho'zilishi, kuchli og'riq.", aid: "Bo'g'imni elastik bint bilan mahkamlash (harakatsiz qilish), muz qo'yish va baland ko'tarish." },
    { name: "Kuyish jarohati", cat: "Travma", desc: "Issiqlik yoki kimyoviy moddalar ta'sirida terining shikastlanishi.", aid: "Kuygan joyni 10-15 daqiqa oqib turgan sovuq suvda tuting, so'ng toza steril bog'lam yoping." },
    { name: "Kesilgan yara", cat: "Travma", desc: "O'tkir buyumlar bilan terining kesilishi va qon ketishi.", aid: "Yarani vodorod peroksid bilan tozalang, atrofiga yod surting va steril bint bilan bog'lang." },
    { name: "Hasharot chaqishi", cat: "Travma", desc: "Ari, chayon yoki boshqa hasharotlar chaqishi, og'riq va shish.", aid: "Nishni pinset bilan sug'urib oling (ari chaqsa), sovuq qo'ying, allergiya dori bering." },
    { name: "Ilon chaqishi", cat: "Travma", desc: "Zaharli ilon tishlashi, tishlangan joyda qattiq og'riq va ko'karish.", aid: "Tishlangan a'zoni harakatsiz saqlang, zahar so'rmang, zudlik bilan tez yordamga yetkazing!" },
    { name: "It qopishi", cat: "Travma", desc: "Hayvon tishlashi natijasida yaralanish, quturish yuqishi xavfi.", aid: "Yarani zudlik bilan kir sovun va ko'p miqdorda suv bilan yuvib tashlang, shifoxonaga boring." },
    { name: "Tomoq bitishi (Laringit)", cat: "Tomoq", desc: "Ovoz boylamlarining yallig'lanishi, ovoz bo'g'ilishi.", aid: "Gapirmaslik, iliq suyuqlik ichish, bug'li ingalyatsiya qilish." },
    { name: "Bosh og'rig'i (Zo'riqish)", cat: "Asab", desc: "Kun davomidagi charchoq va zo'riqish tufayli keladigan bosh og'rig'i.", aid: "Tinchlanish, yetarli uyqu, toza havo, ko'p suv ichish." },
    { name: "Oyoq sinishi (Gips)", cat: "Travma", desc: "Oyoq suyaklarining butunligi buzilishi.", aid: "Oyoqni to'liq harakatsizlantirish, sovuq bosish, zudlik bilan travmatologga borish." },
    { name: "Kuyish (Kimyoviy)", cat: "Travma", desc: "Kimyoviy kislota yoki ishqorlar bilan terining kuyishi.", aid: "Zudlik bilan 20 daqiqa davomida ko'p miqdorda oqib turgan suv bilan yuvish." },
    { name: "Moychechak terapiyasi", cat: "Profilaktika", desc: "Tinchlantiruvchi va yallig'lanishga qarshi o'simlik damlamasi.", aid: "Moychechak gullarini qaynoq suvda damlab, iliq holda ichish yoki tomoq chayish." }
];

// ═══════════════════════════════════════════════════════════════════
// UI LOGIC & EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    renderFirstAidGrid();
    renderDiseases(DISEASES_DATA);
    initSearch();
    initCalculators();
    initOverlay();
    initQuiz();
    initHistory();
});

// TAB SYSTEM
function initTabs() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            navButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// RENDER FIRST AID CARDS
function renderFirstAidGrid() {
    const grid = document.getElementById('first-aid-grid');
    grid.innerHTML = '';
    
    FIRST_AID_ITEMS.forEach(item => {
        const card = document.createElement('div');
        card.className = 'first-aid-card';
        card.setAttribute('data-id', item.id);
        
        card.innerHTML = `
            <div class="card-icon" style="background-color: ${item.bgColor}; color: ${item.color};">
                <i class="fa-solid ${item.icon}"></i>
            </div>
            <h3>${item.title}</h3>
            <p>${item.desc}</p>
        `;
        
        card.addEventListener('click', () => {
            openFirstAidDetail(item);
        });
        
        grid.appendChild(card);
    });
}

// OPEN FIRST AID DETAILS
function openFirstAidDetail(item) {
    const overlay = document.getElementById('overlay-details');
    const title = document.getElementById('overlay-title');
    const body = document.getElementById('overlay-body-content');
    
    title.innerText = item.title;
    
    let stepsHtml = '';
    item.steps.forEach((step, idx) => {
        stepsHtml += `
            <div class="instruction-step">
                <div class="step-num">${idx + 1}</div>
                <div class="step-text">${step}</div>
            </div>
        `;
    });
    
    body.innerHTML = `
        <p style="font-weight: 500; font-size: 15px; margin-bottom: 20px;">${item.desc}</p>
        <h4>🛠️ Bosqichma-bosqich yordam:</h4>
        <div style="margin-top: 12px;">${stepsHtml}</div>
        
        <div class="prohibited-card">
            <h5>⚠️ Mutlaqo taqiqlanadi:</h5>
            <p>${item.prohibited}</p>
        </div>
    `;
    
    overlay.classList.add('active');
}

// RENDER DISEASES
function renderDiseases(data) {
    const container = document.getElementById('disease-list-container');
    container.innerHTML = '';
    
    if (data.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding: 30px; color: var(--hint-color);">Natija topilmadi 😕</div>`;
        return;
    }
    
    data.forEach(item => {
        const div = document.createElement('div');
        div.className = 'disease-item';
        
        div.innerHTML = `
            <div class="disease-info">
                <h4>${item.name}</h4>
                <span>📁 ${item.cat}</span>
            </div>
            <i class="fa-solid fa-chevron-right"></i>
        `;
        
        div.addEventListener('click', () => {
            openDiseaseDetail(item);
        });
        
        container.appendChild(div);
    });
}

// OPEN DISEASE DETAILS
function openDiseaseDetail(item) {
    const overlay = document.getElementById('overlay-details');
    const title = document.getElementById('overlay-title');
    const body = document.getElementById('overlay-body-content');
    
    title.innerText = item.name;
    
    body.innerHTML = `
        <h4 style="margin-top:0;">📚 Kasallik tavsifi:</h4>
        <p style="margin-top: 6px; line-height: 1.6;">${item.desc}</p>
        
        <h4 style="margin-top: 20px; color: var(--button-color);">💡 Birinchi yordam va chora:</h4>
        <p style="margin-top: 6px; line-height: 1.6; background-color: var(--secondary-bg-color); padding: 14px; border-radius: 8px;">
            ${item.aid}
        </p>
    `;
    
    overlay.classList.add('active');
}

// SEARCH FUNCTIONALITY
function initSearch() {
    const input = document.getElementById('disease-search-input');
    const clearBtn = document.getElementById('search-clear-btn');
    
    input.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase().trim();
        
        if (val.length > 0) {
            clearBtn.style.display = 'block';
        } else {
            clearBtn.style.display = 'none';
        }
        
        const filtered = DISEASES_DATA.filter(item => 
            item.name.toLowerCase().includes(val) || 
            item.cat.toLowerCase().includes(val)
        );
        
        renderDiseases(filtered);
    });
    
    clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        renderDiseases(DISEASES_DATA);
    });
}

// OVERLAY CONTROLS
function initOverlay() {
    const closeBtn = document.getElementById('close-overlay-btn');
    const overlay = document.getElementById('overlay-details');
    
    closeBtn.addEventListener('click', () => {
        overlay.classList.remove('active');
    });
}

// CALCULATORS CONTROL
function switchCalc(type) {
    const btns = document.querySelectorAll('.calc-tab-btn');
    const sections = document.querySelectorAll('.calc-section');
    
    btns.forEach(b => b.classList.remove('active'));
    sections.forEach(s => s.classList.remove('active'));
    
    if (type === 'bmi') {
        btns[0].classList.add('active');
        document.getElementById('calc-bmi-section').classList.add('active');
    } else if (type === 'water') {
        btns[1].classList.add('active');
        document.getElementById('calc-water-section').classList.add('active');
    } else {
        btns[2].classList.add('active');
        document.getElementById('calc-calorie-section').classList.add('active');
    }
}

function initCalculators() {
    // BMI
    const btnBmi = document.getElementById('btn-calculate-bmi');
    btnBmi.addEventListener('click', () => {
        const weight = parseFloat(document.getElementById('bmi-weight').value);
        const height = parseFloat(document.getElementById('bmi-height').value);
        
        if (!weight || !height || weight <= 0 || height <= 0) {
            if (tg) tg.showAlert("Iltimos, vazn va bo'y qiymatlarini to'g'ri kiriting!");
            else alert("Iltimos, vazn va bo'y qiymatlarini to'g'ri kiriting!");
            return;
        }
        
        const heightM = height / 100;
        const bmi = weight / (heightM * heightM);
        
        document.getElementById('bmi-number').innerText = bmi.toFixed(1);
        
        // Normal vazn diapazonini hisoblash
        const minW = 18.5 * (heightM * heightM);
        const maxW = 24.9 * (heightM * heightM);
        document.getElementById('bmi-ideal-range').innerText = `${minW.toFixed(1)} - ${maxW.toFixed(1)} kg`;
        
        let status = '';
        let desc = '';
        let pointerPos = 0; // % from left
        
        if (bmi < 18.5) {
            status = "Kam vazn ⚠️";
            desc = "Sizning tana vazningiz me'yordan past. Sog'lom va to'yimli ovqatlanishga harakat qiling.";
            pointerPos = 15;
        } else if (bmi >= 18.5 && bmi < 25) {
            status = "Normal vazn ✅";
            desc = "Sizning vazningiz mutlaqo me'yorda! Faol bo'ling va to'g'ri ovqatlanishda davom eting.";
            pointerPos = 40;
        } else if (bmi >= 25 && bmi < 30) {
            status = "Ortiqcha vazn ⚠️";
            desc = "Tana vazningiz me'yordan bir oz yuqori. Jismoniy mashqlar va shirinliklarni kamaytirish tavsiya etiladi.";
            pointerPos = 65;
        } else {
            status = "Semizlik 🚨";
            desc = "Sizda semizlik darajasi aniqlandi. Sog'lig'ingiz uchun shifokor-dietolog bilan maslahatlashishni tavsiya qilamiz.";
            pointerPos = 90;
        }
        
        document.getElementById('bmi-status').innerText = status;
        document.getElementById('bmi-description').innerText = desc;
        document.getElementById('bmi-gauge-pointer').style.left = `${pointerPos}%`;
        document.getElementById('bmi-result-card').style.display = 'flex';

        // BMI tarixiga saqlash
        saveHistory('bmi', { bmi: bmi.toFixed(1), weight, height, status: status.replace(/[^a-zA-Z\s']/g, '').trim() });
        renderHistoryLog();
    });

    // Water
    const btnWater = document.getElementById('btn-calculate-water');
    btnWater.addEventListener('click', () => {
        const weight = parseFloat(document.getElementById('water-weight').value);
        
        if (!weight || weight <= 0) {
            if (tg) tg.showAlert("Iltimos, vazningizni to'g'ri kiriting!");
            else alert("Iltimos, vazningizni to'g'ri kiriting!");
            return;
        }
        
        const minWater = weight * 30; // ml
        const sportWater = minWater + 500;
        const summerWater = minWater + 300;
        
        document.getElementById('water-value').innerText = `${(minWater / 1000).toFixed(1)} Litr`;
        document.getElementById('water-sport').innerText = `${(sportWater / 1000).toFixed(1)} L`;
        document.getElementById('water-summer').innerText = `${(summerWater / 1000).toFixed(1)} L`;
        
        document.getElementById('water-result-card').style.display = 'flex';

        // Suv tarixiga saqlash
        saveHistory('water', { liters: (minWater / 1000).toFixed(1), weight });
        renderHistoryLog();
    });

    // Calorie
    const btnCalorie = document.getElementById('btn-calculate-calorie');
    btnCalorie.addEventListener('click', () => {
        const gender = document.getElementById('calorie-gender').value;
        const weight = parseFloat(document.getElementById('calorie-weight').value);
        const height = parseFloat(document.getElementById('calorie-height').value);
        const age = parseInt(document.getElementById('calorie-age').value);
        const activity = document.getElementById('calorie-activity').value;
        
        if (!weight || !height || !age || weight <= 0 || height <= 0 || age <= 0) {
            if (tg) tg.showAlert("Iltimos, barcha maydonlarni to'g'ri to'ldiring!");
            else alert("Iltimos, barcha maydonlarni to'g'ri to'ldiring!");
            return;
        }
        
        // Mifflin-St Jeor formula
        let bmr = 0;
        if (gender === 'male') {
            bmr = 10 * weight + 6.25 * height - 5 * age + 5;
        } else {
            bmr = 10 * weight + 6.25 * height - 5 * age - 161;
        }
        
        // TDEE (Total Daily Energy Expenditure)
        let factor = 1.2;
        if (activity === 'moderate') factor = 1.55;
        else if (activity === 'high') factor = 1.9;
        
        const tdee = bmr * factor;
        const lose = tdee - 500;
        const gain = tdee + 500;
        
        document.getElementById('calorie-value').innerText = `${Math.round(tdee)} kkal`;
        document.getElementById('calorie-lose').innerText = `${Math.round(lose)} kkal`;
        document.getElementById('calorie-gain').innerText = `${Math.round(gain)} kkal`;
        
        document.getElementById('calorie-result-card').style.display = 'flex';
    });
}

// ═══════════════════════════════════════════════════════════════════
// QUIZ
// ═══════════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════════
// QUIZ — 65 ta savollik havza, har sessiyada 10 ta tasodifiy
// ═══════════════════════════════════════════════════════════════════

const QUIZ_POOL = [
    { q: "Kuyganda birinchi nima qilish kerak?", options: ["Yog' surish", "Muz qo'yish", "Sovuq suv ostida ushlab turish", "Tish pastasi surtish"], answer: 2 },
    { q: "Qon ketishini to'xtatish uchun qanday bosim o'rnatiladi?", options: ["Yaraning pastki qismiga", "Yaraning yuqori qismiga", "Yara ustiga to'g'ridan-to'g'ri", "Yon tomonga"], answer: 2 },
    { q: "Yurak xurujida bemorni qanday o'tqizish kerak?", options: ["To'liq yotqizish", "Yarim o'tirgan holatda", "Tik turdirish", "Oyoqlarini ko'targan holda yotqizish"], answer: 1 },
    { q: "BMI qanday formulada hisoblanadi?", options: ["Vazn × bo'y", "Vazn / (bo'y²)", "(Vazn + bo'y) / 2", "Vazn - bo'y"], answer: 1 },
    { q: "Normal BMI qiymati qancha?", options: ["10 – 15", "15 – 18.5", "18.5 – 24.9", "25 – 30"], answer: 2 },
    { q: "Tomoqqa narsa tiqilganda qaysi usul qo'llaniladi?", options: ["Geymlix usuli", "CPR usuli", "Turniket usuli", "Shina usuli"], answer: 0 },
    { q: "Tez yordam raqami qancha?", options: ["101", "102", "103", "104"], answer: 2 },
    { q: "Hushidan ketgan bemorning oyoqlari qanday bo'lishi kerak?", options: ["Pastga tushirilgan", "30 sm ko'tarilgan", "Bukib qo'yilgan", "Ikki yon tomonga yozilgan"], answer: 1 },
    { q: "Kislota bilan zaharlanganda qustirish ...", options: ["Foydali", "Zararsiz", "Mutlaqo taqiqlangan", "Ixtiyoriy"], answer: 2 },
    { q: "Issiqlik urganda birinchi navbatda nima qilinadi?", options: ["Bemorga qahva ichirish", "Sovuq vannaga solish", "Soya va salqin joyga olib o'tish", "Gips qo'yish"], answer: 2 },
    { q: "Yong'in xavfsizligi raqami qancha?", options: ["101", "102", "103", "104"], answer: 0 },
    { q: "Turniketni yozda necha soatdan ortiq qoldirish mumkin emas?", options: ["30 daqiqa", "1 soat", "1.5 soat", "3 soat"], answer: 2 },
    { q: "Suyak singanda birinchi nima qilish kerak?", options: ["Suyakni o'z joyiga solish", "Shikastlangan a'zoni harakatsiz qilish", "Issiq kompres qo'yish", "Massaj qilish"], answer: 1 },
    { q: "Insult belgilarida birinchi yordam:", options: ["Bemorni yurgizish", "Yotqizib boshini biroz ko'tarish va 103 chaqirish", "Sovuq suv ichirish", "Dori berish"], answer: 1 },
    { q: "Faollashtirilgan ko'mir har necha kg vazn uchun 1 tabletka beriladi?", options: ["5 kg", "10 kg", "15 kg", "20 kg"], answer: 1 },
    { q: "Noshadir spirti nima uchun ishlatiladi?", options: ["Yaralarni dezinfeksiya qilish", "Hushidan ketgan odamni o'ziga keltirish", "Harorat tushirish", "Og'riq qoldirish"], answer: 1 },
    { q: "Burun qonganda boshni qanday tutish kerak?", options: ["Orqaga eğish", "Oldinga engashtirish", "Yon tomonga burish", "Boshni ko'tarish"], answer: 1 },
    { q: "CPR (yurak-o'pka reanimatsiyasi) qanday bajariladi?", options: ["Ko'krak siqish + sun'iy nafas", "Faqat sun'iy nafas", "Faqat ko'krak siqish", "Orqaga zarba berish"], answer: 0 },
    { q: "Elektr toki ursa birinchi nima qilish kerak?", options: ["Bemorni qo'llar bilan tortish", "Elektr manbaini o'chirish yoki bemorni quruq tayoq bilan itarish", "Suvga yaxshiroq ulash", "Hech narsa qilmay 103 kutish"], answer: 1 },
    { q: "Ilon chaqganda nima QILISH MUMKIN EMAS?", options: ["A'zoni harakatsiz saqlash", "Zaharni og'iz bilan so'rib chiqarish", "103 chaqirish", "Bemorni tinch saqlash"], answer: 1 },
    { q: "Issiqlik urishida tana haroratini qanday tushirish TO'G'RI?", options: ["Muzdek suvli vannaga solish", "Ho'llangan latta bilan artish va salqin joyga o'tkazish", "Sport qilish", "Quyoshda qoldirish"], answer: 1 },
    { q: "Kuygan joyga nima surtish TAQIQLANGAN?", options: ["Steril bog'lam", "Sariyog' yoki tish pastasi", "Sovuq suv", "Toza latta"], answer: 1 },
    { q: "Pufakchali kuyishda pufakchani nima qilish kerak?", options: ["Yorish", "Siqish", "Yormaslik", "Igna bilan teshish"], answer: 2 },
    { q: "Qaysi holat uchun Geymlix usuli qo'llaniladi?", options: ["Qon ketish", "Bo'g'ilish (tomoqqa narsa tiqilish)", "Suyak sinishi", "Kuyish"], answer: 1 },
    { q: "Militsiya raqami qancha?", options: ["101", "102", "103", "1050"], answer: 1 },
    { q: "FVV (Favqulodda vaziyatlar xizmati) raqami qancha?", options: ["101", "102", "103", "1050"], answer: 3 },
    { q: "Ari chaqganda birinchi nima qilish kerak?", options: ["Jarohatni ovqatga bosish", "Nishni pinset bilan chiqarib olish", "Nishni barmoq bilan siqish", "Isitish"], answer: 1 },
    { q: "Miya chayqalishida bemor qanday bo'lishi kerak?", options: ["Tik turishi", "Yugurishi", "Tekis yotishi", "Sakrashi"], answer: 2 },
    { q: "Lat yeyishda (bruise) birinchi chorа:", options: ["Issiq kompres", "Massaj", "Muz qo'yish", "Sport qilish"], answer: 2 },
    { q: "Pay cho'zilganda bo'g'imni nima bilan mahkamlash kerak?", options: ["Ip bilan", "Elastik bint bilan", "Qattiq sim bilan", "Mahkamlash kerak emas"], answer: 1 },
    { q: "Kimyoviy kuyishda yara necha daqiqa suv ostida tutiladi?", options: ["5 daqiqa", "10 daqiqa", "20 daqiqa", "1 daqiqa"], answer: 2 },
    { q: "Zaharlanishda faollashtirilgan ko'mir nima uchun beriladi?", options: ["Og'riqni qoldirish", "Zaharni bog'lash (adsorbtsiya)", "Qon bosimini tushirish", "Isitma tushirish"], answer: 1 },
    { q: "It qopganda yarani birinchi nimalar bilan yuvish kerak?", options: ["Faqat suv bilan", "Kir sovun va ko'p suv bilan", "Spirt bilan", "Yog' bilan"], answer: 1 },
    { q: "Qon bosimi tushib ketganda nima ichirish tavsiya etiladi?", options: ["Sovuq suv", "Iliq shirin choy yoki qahva", "Limon suvi", "Dori"], answer: 1 },
    { q: "Hushsiz odamning og'ziga nima quyish TAQIQLANGAN?", options: ["Havo", "Suv yoki dori", "Suv bug'i", "Hech narsa"], answer: 1 },
    { q: "Kimyoviy modda ko'zga chayqalganda nima qilish kerak?", options: ["Ko'zni ishqalash", "Ko'zni kamida 15-20 daqiqa davomida ko'p miqdorda oqib turgan toza suv bilan yuvish", "Ko'zni bog'lab qo'yish", "Ko'zga tomchi tomizish"], answer: 1 },
    { q: "Muzlagan a'zoni qanday isitish kerak?", options: ["Uni qor bilan ishqalash", "Uni issiq suvga solish", "Asta-sekin iliq muhitda isitish va quruq issiq bog'lam qo'yish", "Olovga yaqin tutish"], answer: 2 },
    { q: "Kuchli qon ketayotganda jgut (turniket) qayerga bog'lanadi?", options: ["Yaraning ustiga", "Yaradan 5-7 sm yuqoriroqqa (yurakka yaqinroq)", "Yaradan pastroqqa", "Bo'g'im ustiga"], answer: 1 },
    { q: "Ochiq suyak sinishida birinchi chora nima?", options: ["Suyakni joyiga kiritish", "Yarani tozalab, steril bog'lam qo'yish va a'zoni harakatsizlantirish (shina qo'yish)", "Shinani to'g'ridan-to'g'ri yalang'och suyakka bog'lash", "Singan joyni massaj qilish"], answer: 1 },
    { q: "Quyosh urganda bemorga qanday suyuqlik berish tavsiya etiladi?", options: ["Muzdek gazlangan suv", "Spirtli ichimliklar", "Oddiy yoki sho'rroq salqin suv", "Achchiq qahva"], answer: 2 },
    { q: "Isitma o'ta yuqori bo'lganda bemorga birinchi yordam sifatida nima qilish mumkin?", options: ["Uni qalin ko'rpaga o'rash", "Tanasini iliq suvda namlangan latta bilan artish va ko'p suyuqlik berish", "Muzdek suvli vannaga yotqizish", "Spirt surtib uxlashga yotqizish"], answer: 1 },
    { q: "Gipertonik krizda (qon bosimi keskin ko'tarilganda) bemorga qanday holat berish kerak?", options: ["Boshini pastga qilib yotqizish", "Yarim o'tirgan holat berish", "Tik turgan holda yurgizish", "Oyoqlarini baland ko'tarib yotqizish"], answer: 1 },
    { q: "Ari chaqqanda allergiya belgisi (shish, nafas qisilishi) bo'lsa, nima qilish kerak?", options: ["Oddiygina muz qo'yib kutish", "Zudlik bilan tez yordam chaqirish va antigistamin dori berish", "Chaqilgan joyni kesish", "Loy surtish"], answer: 1 },
    { q: "Ko'krak qafasiga yot jism kirib qolganda (masalan, pichoq yoki mix):", options: ["Uni tezda sug'urib olish kerak", "Uni joyida qoldirib, qimirlamaydigan qilib mahkamlash va shifokor chaqirish", "Jarohatni kattalashtirib tozalash", "Yarani spirt bilan yuvish"], answer: 1 },
    { q: "Bosh jarohatida bemor hushini yo'qotsa, birinchi navbatda nima qilish kerak?", options: ["Uni o'tirg'izish", "Nafas yo'llari ochiqligini tekshirish va yonbosh holatga yotqizish", "Boshini silkitish", "Yuziga muzdek suv sepib turish"], answer: 1 },
    { q: "CPR (yurak massaji) paytida kattalar uchun ko'krak qafasini bosish chuqurligi qancha bo'lishi kerak?", options: ["1-2 sm", "5-6 sm", "8-10 sm", "Bosish shart emas"], answer: 1 },
    { q: "Tikuv ignasi yoki mayda shisha bo'lagi teriga kirganda va uni ko'rib bo'lmaganda:", options: ["Igna bilan terini chuqur kovlash", "O'z holicha qoldirib, tibbiy yordamga murojaat qilish", "Issiq tuzli suvga solish", "Yarani qattiq siqish"], answer: 1 },
    { q: "Quturish kasalligi qanday yuqadi?", options: ["Faqat havo orqali", "Kasal hayvonning so'lagi shikastlangan teriga yoki yara ustiga tushganda (tishlaganda)", "Muloqot paytida ko'z orqali", "Faqat iflos suv ichganda"], answer: 1 },
    { q: "Qon ketganda yaraning ustiga qanday mato qo'yish kerak?", options: ["Rangli jun mato", "Steril doka (bint) yoki imkon qadar eng toza mato", "Quruq barglar", "Gazeta qog'ozi"], answer: 1 },
    { q: "Turniket (jgut) yozilgan qog'ozda nima yozilishi shart?", options: ["Bemoring ismi va yoshi", "Turniket bog'langan aniq vaqt (soat va daqiqa)", "Qon guruhi", "Tez yordam chaqirilgan vaqt"], answer: 1 },
    { q: "Gazdan zaharlangan odamni birinchi navbatda nima qilish kerak?", options: ["Unga suv ichirish", "Zudlik bilan toza havoga olib chiqish", "Yuragiga muz qo'yish", "Uni uxlashga yotqizish"], answer: 1 },
    { q: "Tok urgan odam hushida bo'lsa va tashqi jarohati bo'lmasa:", options: ["Unga darhol ruxsat berish", "Baribir shifokor ko'rigidan o'tkazish (yurak ritmi buzilishi mumkin)", "Unga dori berib yotqizish", "Sovuq suvda yuvintirish"], answer: 1 },
    { q: "Termik kuyishda (issiq suv yoki olovda) kiyim teriga yopishib qolsa:", options: ["Uni kuch bilan yulib olish", "Kiyimni yulmasdan, atrofini kesib olish va shifokorga murojaat qilish", "Ustidan yog' surtish", "Hech narsa qilmaslik"], answer: 1 },
    { q: "Qorin sohasida kuchli o'tkir og'riq bo'lganda (masalan, appenditsit shubhasida) nima qilish mumkin emas?", options: ["Tez yordam chaqirish", "Og'riq qoldiruvchi dori ichish va qoringa issiq narsa qo'yish", "Bemorni tinch holatda yotqizish", "Ovqat va suv bermaslik"], answer: 1 },
    { q: "Sovuq urgan tana a'zosini (masalan, barmoqlarni) uqalash orqali isitish...", options: ["Foydali, qon yurishadi", "Taqiqlanadi, chunki yumshoq to'qimalarga jiddiy shikast yetishi mumkin", "Zararsiz", "Faqat bolalarda mumkin"], answer: 1 },
    { q: "Bola tomoqqa narsa tiqilib ko'karib ketganda nima qilinadi (1 yoshgacha)?", options: ["Oyoqlaridan ko'tarib silkitish", "Qornidan quchoqlab Geymlix qilish", "Uni bilakka yuzini pastga qilib yotqizib, kuraklariga asta 5 marta urish", "Og'ziga suv quyish"], answer: 2 },
    { q: "Yurak xurujida aspirin dori vositasini bemorga qanday bergan ma'qul?", options: ["Butunlay yuttirish", "Chaynashni so'rash (tezroq so'rilishi uchun)", "Suvda eritib ichirish", "Aspirin berish mutlaqo mumkin emas"], answer: 1 },
    { q: "Epilepsiya (tutqanoq) xuruji paytida bemorning og'ziga qoshiq yoki qattiq jism tiqish...", options: ["Taqiqlanadi, tishlari va jag'iga zarar yetishi mumkin", "Tavsiya etiladi, tilini tishlab olmasligi uchun", "Faqat kattalarda ruxsat beriladi", "Zararsiz"], answer: 0 },
    { q: "Burun qonashida paxtani vodorod peroksid bilan ho'llab burunga qo'yish...", options: ["Zararli", "Yordam beradi (qonni to'xtatishga yordam beradi)", "Mutlaqo taqiqlangan", "Faqat shifokor qilishi kerak"], answer: 1 },
    { q: "Quyosh ostida uzoq vaqt bosh kiyimsiz yurish qanday oqibatga olib keladi?", options: ["Grippga", "Quyosh urishiga (issiqlik urishi)", "Gastritga", "Anemiyaga"], answer: 1 },
    { q: "Kattalarda yurak massaji soni va sun'iy nafas nisbati qanday bo'ladi?", options: ["15 ta bosish va 2 ta nafas", "30 ta bosish va 2 ta nafas", "10 ta bosish va 1 ta nafas", "5 ta bosish va 5 ta nafas"], answer: 1 },
    { q: "Kimyoviy modda teriga to'kilsa, suv bilan yuvishdan oldin nima qilish kerak?", options: ["Ustidan kukun sepish", "Quruq salfetka yoki mato bilan moddani ehtiyotkorlik bilan artib tashlash (agar u suv bilan reaksiyaga kirsa)", "Yog' surtish", "Hech narsa qilmasdan darhol suv quyish"], answer: 1 },
    { q: "Jarohatdan ko'piksimon, och qizil rangli qon otilib chiqayotgan bo'lsa, bu qanday qon ketish?", options: ["Venoz qon ketish", "Arterial qon ketish", "Kapillyar qon ketish", "Aralash qon ketish"], answer: 1 },
    { q: "Shikastlangan odamni ko'chirish yoki tashish qachon majburiy hisoblanadi?", options: ["Har qanday holatda darhol", "Faqat u yerda qolish bemor hayotiga xavf tug'dirganda (masalan, yong'in, qulash xavfi)", "Faqat bemor o'zi so'raganda", "Hech qachon mumkin emas"], answer: 1 },
    { q: "Hushidan ketgan odamni yonbosh (xavfsiz) holatga o'tkazishdan maqsad nima?", options: ["Uxlashini osonlashtirish", "Nafas yo'llari til orqaga ketishi yoki qusiq moddalari bilan to'silib qolishini oldini olish", "Og'riqni kamaytirish", "Qon bosimini ko'tarish"], answer: 1 },
];

// Massivni aralashtiruvchi funksiya (Fisher-Yates shuffle)
function shuffleArray(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

// Savollar havzasidan 10 tani tasodifiy tanlab, variantlarini ham aralashtirib chiqaradi
function buildRandomQuiz(count = 10) {
    const picked = shuffleArray(QUIZ_POOL).slice(0, count);
    return picked.map(q => {
        // Har bir savol uchun variantlarni indeksi bilan birgalikda olish
        const indexed = q.options.map((opt, idx) => ({ opt, isCorrect: idx === q.answer }));
        const shuffled = shuffleArray(indexed);
        const newCorrect = shuffled.findIndex(o => o.isCorrect);
        return {
            q: q.q,
            options: shuffled.map(o => o.opt),
            answer: newCorrect
        };
    });
}

let QUIZ_QUESTIONS = buildRandomQuiz();
let quizState = { current: 0, score: 0, answered: false };

function initQuiz() {
    updateQuizStats();
    document.getElementById('btn-start-quiz').addEventListener('click', startQuiz);
    document.getElementById('btn-retry-quiz').addEventListener('click', startQuiz);
}

function updateQuizStats() {
    const best = parseInt(localStorage.getItem('quiz_best') || '0');
    const attempts = parseInt(localStorage.getItem('quiz_attempts') || '0');
    document.getElementById('quiz-best-score').innerText = best;
    document.getElementById('quiz-attempts').innerText = attempts;
}

function showQuizScreen(id) {
    document.querySelectorAll('.quiz-screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

function startQuiz() {
    // Har safar yangi tasodifiy savollar va aralash variantlar
    QUIZ_QUESTIONS = buildRandomQuiz(10);
    quizState = { current: 0, score: 0, answered: false };
    showQuizScreen('quiz-question-screen');
    renderQuizQuestion();
}

function renderQuizQuestion() {
    const q = QUIZ_QUESTIONS[quizState.current];
    const total = QUIZ_QUESTIONS.length;
    document.getElementById('quiz-q-num').innerText = `Savol ${quizState.current + 1}/${total}`;
    document.getElementById('quiz-score-live').innerText = `\uD83C\uDFAF ${quizState.score} ball`;
    document.getElementById('quiz-progress-fill').style.width = `${((quizState.current + 1) / total) * 100}%`;
    document.getElementById('quiz-question-text').innerText = q.q;

    const container = document.getElementById('quiz-options-container');
    container.innerHTML = '';
    quizState.answered = false;

    q.options.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'quiz-option-btn';
        btn.innerText = opt;
        btn.addEventListener('click', () => handleAnswer(idx, btn));
        container.appendChild(btn);
    });
}

function handleAnswer(idx, btn) {
    if (quizState.answered) return;
    quizState.answered = true;

    const correct = QUIZ_QUESTIONS[quizState.current].answer;
    const allBtns = document.querySelectorAll('.quiz-option-btn');

    allBtns.forEach(b => b.disabled = true);

    if (idx === correct) {
        btn.classList.add('correct');
        quizState.score += 10;
    } else {
        btn.classList.add('wrong');
        allBtns[correct].classList.add('correct');
    }

    setTimeout(() => {
        quizState.current++;
        if (quizState.current < QUIZ_QUESTIONS.length) {
            renderQuizQuestion();
        } else {
            finishQuiz();
        }
    }, 1000);
}

function finishQuiz() {
    const score = quizState.score;
    const best = parseInt(localStorage.getItem('quiz_best') || '0');
    const attempts = parseInt(localStorage.getItem('quiz_attempts') || '0');
    if (score > best) localStorage.setItem('quiz_best', score);
    localStorage.setItem('quiz_attempts', attempts + 1);

    let icon = '\uD83D\uDE22', title = 'Ko\'proq o\'qing!', desc = 'Hali siz uchun o\'rganish vaqti!';
    if (score >= 80) { icon = '\uD83C\uDFC6'; title = 'Barakallo!'; desc = 'Siz juda yaxshi bilasiz!'; }
    else if (score >= 50) { icon = '\uD83D\uDCAA'; title = 'Yaxshi natija!'; desc = 'Ozgina ko\'proq o\'qisangiz mukammal bo\'ladi!'; }

    document.getElementById('quiz-result-icon').innerText = icon;
    document.getElementById('quiz-result-title').innerText = title;
    document.getElementById('quiz-final-score-num').innerText = score;
    document.getElementById('quiz-result-desc').innerText = desc;
    showQuizScreen('quiz-result-screen');
    updateQuizStats();
}

// ═══════════════════════════════════════════════════════════════════
// HISTORY (LocalStorage + Canvas Chart)
// ═══════════════════════════════════════════════════════════════════

function saveHistory(type, data) {
    const key = `history_${type}`;
    const arr = JSON.parse(localStorage.getItem(key) || '[]');
    const now = new Date();
    const dateStr = `${now.getDate()}.${now.getMonth()+1}.${now.getFullYear()}`;
    arr.push({ date: dateStr, ...data });
    if (arr.length > 30) arr.shift(); // max 30 ta yozuv
    localStorage.setItem(key, JSON.stringify(arr));
}

function initHistory() {
    renderHistoryLog();
    document.getElementById('btn-clear-bmi-history').addEventListener('click', () => {
        localStorage.removeItem('history_bmi');
        renderHistoryLog();
    });
    document.getElementById('btn-clear-water-history').addEventListener('click', () => {
        localStorage.removeItem('history_water');
        renderHistoryLog();
    });
}

function switchHistoryTab(type) {
    document.querySelectorAll('.history-tab-btn').forEach((b, i) => {
        b.classList.toggle('active', (i === 0 && type === 'bmi') || (i === 1 && type === 'water'));
    });
    document.getElementById('history-bmi').classList.toggle('active', type === 'bmi');
    document.getElementById('history-water').classList.toggle('active', type === 'water');
    drawChart(type);
}

function renderHistoryLog() {
    renderBmiLog();
    renderWaterLog();
    drawChart('bmi');
    drawChart('water');
}

function renderBmiLog() {
    const arr = JSON.parse(localStorage.getItem('history_bmi') || '[]').slice().reverse();
    const log = document.getElementById('bmi-history-log');
    const empty = document.getElementById('bmi-chart-empty');
    log.innerHTML = '';
    if (arr.length === 0) { empty.style.display = 'flex'; return; }
    empty.style.display = 'none';
    arr.forEach(entry => {
        const badgeClass = parseFloat(entry.bmi) < 18.5 ? 'low' : parseFloat(entry.bmi) < 25 ? 'normal' : 'high';
        const badgeText = parseFloat(entry.bmi) < 18.5 ? 'Kam' : parseFloat(entry.bmi) < 25 ? 'Normal' : 'Yuqori';
        log.innerHTML += `
        <div class="history-log-item">
            <span class="h-date">${entry.date}</span>
            <span class="h-val">BMI: ${entry.bmi}</span>
            <span class="h-badge ${badgeClass}">${badgeText}</span>
        </div>`;
    });
}

function renderWaterLog() {
    const arr = JSON.parse(localStorage.getItem('history_water') || '[]').slice().reverse();
    const log = document.getElementById('water-history-log');
    const empty = document.getElementById('water-chart-empty');
    log.innerHTML = '';
    if (arr.length === 0) { empty.style.display = 'flex'; return; }
    empty.style.display = 'none';
    arr.forEach(entry => {
        log.innerHTML += `
        <div class="history-log-item">
            <span class="h-date">${entry.date}</span>
            <span class="h-val">${entry.liters} L</span>
            <span class="h-badge normal">Hisoblandi</span>
        </div>`;
    });
}

function drawChart(type) {
    const canvasId = type === 'bmi' ? 'bmi-chart' : 'water-chart';
    const key = `history_${type}`;
    const arr = JSON.parse(localStorage.getItem(key) || '[]');
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');

    canvas.width = canvas.parentElement.clientWidth - 32;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (arr.length < 2) return;

    const values = arr.map(e => parseFloat(type === 'bmi' ? e.bmi : e.liters));
    const labels = arr.map(e => e.date);
    const min = Math.min(...values) * 0.9;
    const max = Math.max(...values) * 1.1;
    const w = canvas.width;
    const h = canvas.height;
    const pad = { top: 16, bottom: 30, left: 10, right: 10 };
    const chartW = w - pad.left - pad.right;
    const chartH = h - pad.top - pad.bottom;

    const xStep = chartW / (values.length - 1);
    const toX = i => pad.left + i * xStep;
    const toY = v => pad.top + chartH - ((v - min) / (max - min || 1)) * chartH;

    // Gradient fill
    const grad = ctx.createLinearGradient(0, pad.top, 0, h - pad.bottom);
    grad.addColorStop(0, 'rgba(0,122,255,0.25)');
    grad.addColorStop(1, 'rgba(0,122,255,0.01)');

    ctx.beginPath();
    ctx.moveTo(toX(0), toY(values[0]));
    values.forEach((v, i) => { if (i > 0) ctx.lineTo(toX(i), toY(v)); });
    ctx.lineTo(toX(values.length - 1), h - pad.bottom);
    ctx.lineTo(toX(0), h - pad.bottom);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Line
    ctx.beginPath();
    ctx.moveTo(toX(0), toY(values[0]));
    values.forEach((v, i) => { if (i > 0) ctx.lineTo(toX(i), toY(v)); });
    ctx.strokeStyle = '#007aff';
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.stroke();

    // Dots and labels
    values.forEach((v, i) => {
        ctx.beginPath();
        ctx.arc(toX(i), toY(v), 4, 0, Math.PI * 2);
        ctx.fillStyle = '#007aff';
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Date labels (every 2nd if many)
        if (arr.length <= 7 || i % 2 === 0) {
            ctx.fillStyle = '#888';
            ctx.font = '9px Outfit, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(labels[i], toX(i), h - 6);
        }
    });
}
