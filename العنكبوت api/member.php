<?php
$link = "https://t.me/$botUser?start=$id";
$lang = array(
	 "ar" => "العربية 🇸🇦" ,
	 "en" => "English 🇺🇲",
	 "ru" => "Русский 🇷🇺",
	 "fa" => "فارسى 🇮🇷",
	 "cht" => "繁體中文 🇨🇳",
	 "chb" => "简体中文 🇨🇳"
);
#---------------------------------------الترجمة---------------------------------------------
$trans = array(
	"ar" => array(
		"1" => "اضغط للتحقق",
		"2" =>  "🖐︙مرحبا بك

- يجب الإشتراك بقناة البوت الرسمية لإستخدام البوت 
- رابط القناة: $ch6

🙋‍♂️ ⁞ إضغط على الزر بالأسفل للتحقق",
		"3" => "لا يمكنك استخدام البوت لانك محظور",
		"4" => " تم دخول عضو عن طريق رابطك وقد ربحت  __invitePoint__",
		"5" => "٭ شـراء حسابات Telegram ٭",
		"6" => "٭ اشحن رصيدك ٭",
		"7" => "٭ فريق ألدعم ٭",
		"8" => "٭ الوكـلاء ٭",
		"9" => "٭ تفعيلات البوت ٭",
		"10" => "٭ ربح رصيد مجــاني ٭",
		"11" => "- السَلام عليكُم مرحبا بك في بوت حسابات التيليجرام .

- تستطيع ان تحصل بسهولة على رقم افتراضي مع حسابات التليجرام الجاهزة ، بسرعة خيالية .. تلقائي بالكامل ، بأقل سعر ممكن ، متوفر دعم على مدار 24 ساعة .

- ايدي حسابك : <code>$id</code>
- رصيدك : $point$",
		"12" => "
لشحن حسابك قم بالتواصل مع الادارة @Y_O_Ul
او بالتواصل مع احد الوكلاء في البوت
		",
		"13" => "
في حالة واجهت اي مشكلة قم بالتواصل معنا عبر اليوزر التالي 
@Y_O_Ul	
		",
		"14" => "
لا يوجد وكلاء في البوت في الوقت الحالي
		",
		"15" => "
قم بدعوة اصدقائك على الرابط التالي  واكسب $invitePoint على كل شخص ينضم  بواسطتك


<code> $link</code>
		",
		"16" => "
الدول المتاحة\n
		",
		"17" => "
لا توجد قائمة تالية
		",
		"18" => "
لا توجد قائمة سابقة
		",
		"19" => "
	يرجى إختيار الدولة التي تريد شراء حساب منها•

جميع الدول في الأسفل تمتلك حسابات لتفعيل التيليجرام ، وتستقبل وصول الكود على أي نسخة ، إضغط على الدولة للشراء •
		",
		"20" => "السابق",
		"21" => "التالي",
		"22" => "تاكيد الشراء",
		"23" => "
شروط إخلاء المسؤوليه

عزيزي العميل بعد موافقتك والظغط على زر الشراء يتم خصم قيمة الرقم ويعتبر الرقم هو ملك لك ولن يتم استرداد الأموال.

هل تريد شراء رقم

		",
		"24" => "لا توجد ارقام لهذه الدولة في الوقت الحالي✖️",		
		"25" => "
✅- تم شراء حساب تيليجرام بنجاح -✅

🌎 - الدولة: __c__
☎️ - الرقم: <code>__num__</code>
💰- السعر :  __p__"."$
💬 - الكود : ××××
🔑 - كلمة المرور: ××××××

- يرجى تسجيل الرقم في تيليجرام ، بعد التسجيل ، إضغط على ( طلب الكود  ) للحصول على كود التفعيل .

		",
		"26" => "طلب الكود",
		"27" => "رصيدك غير كافي",
		"28" => "لم يصل الكود بعد",
		"29" => "
💬- تم وصول الكود في الاسفل •

🌎 - الدولة: __c__
☎️ - الرقم: <code>__num__</code>
💰- السعر :  __p__"."$
💬 - الكود : <code>__code__</code>
🔑 - كلمة المرور: <code>__pass__</code>

✅- قم بتفعيل الرقم في تطبيق تيليجرام ✳️
",
		
	),
	 "en" => array(
    "1" => "Click to verify",
    "2" => "🖐︙Welcome

- You must subscribe to the official bot channel to use the bot
- Channel link: $ch6

🙋‍♂️ ⁞ Click the button below to verify",
    "3" => "You cannot use the bot because you are banned.",
    "4" => "A member has joined through your link, and you have earned __invitePoint__.",
    "5" => "* Purchase Telegram Accounts *",
    "6" => "* Recharge Your Balance *",
    "7" => "* Support Team *",
    "8" => "* Agents *",
    "9" => "* Bot Activations *",
    "10" => "* Win Free Balance *",
    "11" => "- Hello, welcome to the Telegram accounts bot.

- You can easily get a virtual number with ready-made Telegram accounts, at an incredible speed.. fully automated, at the lowest possible price, with 24/7 support.

- Your account ID: <code>$id</code>
- Your balance: $point$",
    "12" => "
To recharge your account, please contact the administration @Ba_ageel
or contact one of the agents in the bot
    ",
    "13" => "
If you encounter any issues, please contact us via the following username 
@Ba_ageel    
    ",
    "14" => "
There are no agents in the bot at this time
    ",
    "15" => "
Invite your friends using the following link and earn $invitePoint for every person who joins through you

<code> $link</code>
    ",
    "16" => "
Available countries\n
    ",
    "17" => "
No next list available
    ",
    "18" => "
No previous list available
    ",
    "19" => "
Please choose the country you want to buy an account from•

All countries listed below have accounts for activating Telegram, and receive code access on any version, click the country to purchase •
    ",
    "20" => "Previous",
    "21" => "Next",
    "22" => "Confirm Purchase",
    "23" => "
Disclaimer Conditions

Dear customer, after you agree and click the purchase button, the value of the number will be deducted, and the number will be yours and will not be refunded.

Do you want to purchase a number
    ",
    "24" => "There are no numbers available for this country at the moment✖️",
    "25" => "
✅- Telegram account purchased successfully -✅

🌎 - Country: __c__
☎️ - Number: <code>__num__</code>
💰- Price: __p__"."$
💬 - Code: ××××
🔑 - Password: ××××××

- Please register the number in Telegram. After registration, click (Request Code) to get the activation code.
    ",
    "26" => "Request Code",
    "27" => "Your balance is insufficient",
    "28" => "The code has not arrived yet",
    "29" => "
💬- The code has arrived below •

🌎 - Country: __c__
☎️ - Number: <code>__num__</code>
💰- Price: __p__"."$
💬 - Code: <code>__code__</code>
🔑 - Password: <code>__pass__</code>

✅- Please activate the number in the Telegram app ✳️
",
),
"ru" => array(
    "1" => "Нажмите для проверки",
    "2" => "🖐︙Добро пожаловать

- Вы должны подписаться на официальный канал бота, чтобы использовать бота
- Ссылка на канал: $ch6

🙋‍♂️ ⁞ Нажмите кнопку ниже, чтобы подтвердить",
    "3" => "Вы не можете использовать бота, потому что вы забанены.",
    "4" => "Член присоединился по вашей ссылке, и вы заработали __invitePoint__.",
    "5" => "* Покупка аккаунтов Telegram *",
    "6" => "* Пополните свой баланс *",
    "7" => "* Команда поддержки *",
    "8" => "* Агенты *",
    "9" => "* Активации бота *",
    "10" => "* Выиграйте бесплатный баланс *",
    "11" => "- Здравствуйте, добро пожаловать в бот аккаунтов Telegram.

- Вы можете легко получить виртуальный номер с готовыми аккаунтами Telegram, с невероятной скоростью.. полностью автоматически, по самой низкой цене, с поддержкой 24/7.

- Ваш ID аккаунта: <code>$id</code>
- Ваш баланс: $point$",
    "12" => "
Чтобы пополнить свой счет, пожалуйста, свяжитесь с администрацией @Ba_ageel
или свяжитесь с одним из агентов в боте
    ",
    "13" => "
Если у вас возникли проблемы, свяжитесь с нами по следующему имени пользователя 
@Ba_ageel    
    ",
    "14" => "
В данный момент в боте нет агентов
    ",
    "15" => "
Пригласите своих друзей по следующей ссылке и заработайте $invitePoint за каждого человека, который присоединится через вас

<code> $link</code>
    ",
    "16" => "
Доступные страны\n
    ",
    "17" => "
Нет следующего списка
    ",
    "18" => "
Нет предыдущего списка
    ",
    "19" => "
Пожалуйста, выберите страну, из которой вы хотите купить аккаунт•

Все страны, указанные ниже, имеют аккаунты для активации Telegram и получают доступ к коду на любой версии, нажмите на страну, чтобы купить •
    ",
    "20" => "Предыдущий",
    "21" => "Следующий",
    "22" => "Подтвердить покупку",
    "23" => "
Условия отказа от ответственности

Уважаемый клиент, после того как вы согласитесь и нажмете кнопку покупки, стоимость номера будет снята, и номер станет вашим, и деньги не будут возвращены.

Вы хотите купить номер
    ",
    "24" => "В данный момент нет номеров для этой страны✖️",
    "25" => "
✅- Аккаунт Telegram успешно куплен -✅

🌎 - Страна: __c__
☎️ - Номер: <code>__num__</code>
💰- Цена: __p__"."$
💬 - Код: ××××
🔑 - Пароль: ××××××

- Пожалуйста, зарегистрируйте номер в Telegram. После регистрации нажмите (Запросить код), чтобы получить код активации.
    ",
    "26" => "Запросить код",
    "27" => "Ваш баланс недостаточен",
    "28" => "Код еще не пришел",
    "29" => "
💬- Код пришел ниже •

🌎 - Страна: __c__
☎️ - Номер: <code>__num__</code>
💰- Цена: __p__"."$
💬 - Код: <code>__code__</code>
🔑 - Пароль: <code>__pass__</code>

✅- Пожалуйста, активируйте номер в приложении Telegram ✳️
",
),


	 "fa" => array(
    "1" => "برای تأیید کلیک کنید",
    "2" => "🖐︙خوش آمدید

- برای استفاده از ربات، باید به کانال رسمی ربات عضو شوید
- لینک کانال: $ch6

🙋‍♂️ ⁞ برای تأیید، روی دکمه زیر کلیک کنید",
    "3" => "شما نمی‌توانید از ربات استفاده کنید زیرا شما مسدود شده‌اید.",
    "4" => "یک عضو از طریق لینک شما وارد شده است و شما __invitePoint__ برنده شده‌اید.",
    "5" => "* خرید حساب‌های تلگرام *",
    "6" => "* موجودی خود را شارژ کنید *",
    "7" => "* تیم پشتیبانی *",
    "8" => "* نمایندگان *",
    "9" => "* فعال‌سازی‌های ربات *",
    "10" => "* برنده شدن موجودی رایگان *",
    "11" => "- سلام، خوش آمدید به ربات حساب‌های تلگرام.

- شما می‌توانید به راحتی یک شماره مجازی با حساب‌های تلگرام آماده دریافت کنید، با سرعتی شگفت‌انگیز.. به‌طور کامل خودکار، با پایین‌ترین قیمت ممکن، با پشتیبانی ۲۴ ساعته.

- شناسه حساب شما: <code>$id</code>
- موجودی شما: $point$",
    "12" => "
برای شارژ حساب خود، لطفاً با مدیریت @Ba_ageel تماس بگیرید
یا با یکی از نمایندگان در ربات تماس بگیرید
    ",
    "13" => "
اگر با مشکلی مواجه شدید، لطفاً با ما از طریق نام کاربری زیر تماس بگیرید 
@Ba_ageel    
    ",
    "14" => "
در حال حاضر نماینده‌ای در ربات وجود ندارد
    ",
    "15" => "
دوستان خود را با استفاده از لینک زیر دعوت کنید و به ازای هر شخصی که از طریق شما به جمع می‌پیوندد $invitePoint دریافت کنید

<code> $link</code>
    ",
    "16" => "
کشورهای موجود\n
    ",
    "17" => "
لیست بعدی موجود نیست
    ",
    "18" => "
لیست قبلی موجود نیست
    ",
    "19" => "
لطفاً کشوری را که می‌خواهید حسابی از آن خریداری کنید انتخاب کنید•

تمام کشورهایی که در زیر ذکر شده‌اند حساب‌هایی برای فعال‌سازی تلگرام دارند و کد را بر روی هر نسخه‌ای دریافت می‌کنند، برای خرید بر روی کشور کلیک کنید •
    ",
    "20" => "قبلی",
    "21" => "بعدی",
    "22" => "تأیید خرید",
    "23" => "
شرایط سلب مسئولیت

مشتری عزیز، پس از اینکه شما موافقت کردید و روی دکمه خرید کلیک کردید، مبلغ شماره کسر شده و شماره متعلق به شما خواهد بود و وجهی بازگشت داده نخواهد شد.

آیا می‌خواهید شماره‌ای خریداری کنید
    ",
    "24" => "در حال حاضر شماره‌ای برای این کشور موجود نیست✖️",
    "25" => "
✅- حساب تلگرام با موفقیت خریداری شد -✅

🌎 - کشور: __c__
☎️ - شماره: <code>__num__</code>
💰- قیمت: __p__"."$
💬 - کد: ××××
🔑 - کلمه عبور: ××××××

- لطفاً شماره را در تلگرام ثبت کنید. پس از ثبت‌نام، روی (درخواست کد) کلیک کنید تا کد فعال‌سازی را دریافت کنید.
    ",
    "26" => "درخواست کد",
    "27" => "موجودی شما کافی نیست",
    "28" => "کد هنوز نرسیده است",
    "29" => "
💬- کد در پایین آمده است •

🌎 - کشور: __c__
☎️ - شماره: <code>__num__</code>
💰- قیمت: __p__"."$
💬 - کد: <code>__code__</code>
🔑 - کلمه عبور: <code>__pass__</code>

✅- لطفاً شماره را در برنامه تلگرام فعال کنید ✳️
",
),


	
	 "cht" => array(
    "1" => "點擊以驗證",
    "2" => "🖐︙歡迎

- 您必須訂閱官方機器人頻道才能使用機器人
- 頻道鏈接：$ch6

🙋‍♂️ ⁞ 點擊下方按鈕進行驗證",
    "3" => "您無法使用機器人，因為您已被禁止。",
    "4" => "有成員通過您的連結加入，您贏得了 __invitePoint__。",
    "5" => "* 購買 Telegram 帳戶 *",
    "6" => "* 充值您的餘額 *",
    "7" => "* 支持團隊 *",
    "8" => "* 代理商 *",
    "9" => "* 機器人激活 *",
    "10" => "* 贏取免費餘額 *",
    "11" => "- 您好，歡迎來到 Telegram 帳戶機器人。

- 您可以輕鬆獲得虛擬號碼和現成的 Telegram 帳戶，以驚人的速度.. 完全自動化，以最低的價格，提供 24/7 支持。

- 您的帳號 ID：<code>$id</code>
- 您的餘額：$point$",
    "12" => "
要充值您的帳戶，請聯繫管理員 @Ba_ageel
或聯繫機器人中的一位代理商
    ",
    "13" => "
如果您遇到任何問題，請通過以下用戶名與我們聯繫 
@Ba_ageel    
    ",
    "14" => "
目前機器人中沒有代理商
    ",
    "15" => "
邀請您的朋友使用以下鏈接，每位通過您加入的人您將獲得 $invitePoint

<code> $link</code>
    ",
    "16" => "
可用國家\n
    ",
    "17" => "
沒有下一個列表
    ",
    "18" => "
沒有上一個列表
    ",
    "19" => "
請選擇您想購買帳戶的國家•

所有列出的國家都有可用於激活 Telegram 的帳戶，並在任何版本上接收代碼，點擊該國以進行購買 •
    ",
    "20" => "上一個",
    "21" => "下一個",
    "22" => "確認購買",
    "23" => "
免責聲明條款

親愛的客戶，當您同意並點擊購買按鈕後，將扣除號碼的費用，該號碼將屬於您且不會退款。

您想購買號碼嗎
    ",
    "24" => "目前此國家沒有可用的號碼✖️",
    "25" => "
✅- Telegram 帳戶成功購買 -✅

🌎 - 國家: __c__
☎️ - 號碼: <code>__num__</code>
💰- 價格: __p__"."$
💬 - 代碼: ××××
🔑 - 密碼: ××××××

- 請在 Telegram 中註冊該號碼。註冊後，點擊（請求代碼）以獲取激活代碼。
    ",
    "26" => "請求代碼",
    "27" => "您的餘額不足",
    "28" => "代碼尚未到達",
    "29" => "
💬- 代碼已到達如下 •

🌎 - 國家: __c__
☎️ - 號碼: <code>__num__</code>
💰- 價格: __p__"."$
💬 - 代碼: <code>__code__</code>
🔑 - 密碼: <code>__pass__</code>

✅- 請在 Telegram 應用中激活該號碼 ✳️
",
),

	 "chb" => array(
    "1" => "点击以验证",
    "2" => "🖐︙欢迎

- 您必须订阅官方机器人频道才能使用机器人
- 频道链接：$ch6

🙋‍♂️ ⁞ 点击下方按钮进行验证",
    "3" => "您无法使用机器人，因为您已被禁止。",
    "4" => "有成员通过您的链接加入，您赢得了 __invitePoint__。",
    "5" => "* 购买 Telegram 账户 *",
    "6" => "* 充值您的余额 *",
    "7" => "* 支持团队 *",
    "8" => "* 代理商 *",
    "9" => "* 机器人激活 *",
    "10" => "* 赢取免费余额 *",
    "11" => "- 您好，欢迎来到 Telegram 账户机器人。

- 您可以轻松获得虚拟号码和现成的 Telegram 账户，以惊人的速度.. 完全自动化，以最低的价格，提供 24/7 支持。

- 您的账户 ID：<code>$id</code>
- 您的余额：$point$",
    "12" => "
要充值您的账户，请联系管理员 @Ba_ageel
或联系机器人中的一位代理商
    ",
    "13" => "
如果您遇到任何问题，请通过以下用户名与我们联系 
@Ba_ageel    
    ",
    "14" => "
目前机器人中没有代理商
    ",
    "15" => "
邀请您的朋友使用以下链接，每位通过您加入的人您将获得 $invitePoint

<code> $link</code>
    ",
    "16" => "
可用国家\n
    ",
    "17" => "
没有下一个列表
    ",
    "18" => "
没有上一个列表
    ",
    "19" => "
请选择您想购买账户的国家•

所有列出的国家都有用于激活 Telegram 的账户，并在任何版本上接收代码，点击该国以进行购买 •
    ",
    "20" => "上一个",
    "21" => "下一个",
    "22" => "确认购买",
    "23" => "
免责声明条款

亲爱的客户，当您同意并点击购买按钮后，将扣除号码的费用，该号码将属于您且不会退款。

您想购买号码吗
    ",
    "24" => "目前此国家没有可用的号码✖️",
    "25" => "
✅- Telegram 账户购买成功 -✅

🌎 - 国家: __c__
☎️ - 号码: <code>__num__</code>
💰- 价格: __p__"."$
💬 - 代码: ××××
🔑 - 密码: ××××××

- 请在 Telegram 中注册该号码。注册后，点击（请求代码）以获取激活代码。
    ",
    "26" => "请求代码",
    "27" => "您的余额不足",
    "28" => "代码尚未到达",
    "29" => "
💬- 代码已到达如下 •

🌎 - 国家: __c__
☎️ - 号码: <code>__num__</code>
💰- 价格: __p__"."$
💬 - 代码: <code>__code__</code>
🔑 - 密码: <code>__pass__</code>

✅- 请在 Telegram 应用中激活该号码 ✳️
",
)
);
#------------------------------------------------------------------------------------
$langs = json_decode(file_get_contents("langs.json"),1)??[];
function saveLangs(){
	global $langs;
	if($langs != null )
	file_put_contents("langs.json",json_encode($langs,448));
}
if($ex[0] == "/start") {
	if(!isset($points[$id]) && isset($points[$ex[1]]) && $id !=  $ex[1]){
		$invite['whoInvitedMe'][$id] = $ex[1];
		saveInvite();
	}
}
$z=array(
	 "ar" => "رجوع" ,
	 "en" => "Back",
	 "ru" => "Назад",
	 "fa" => "بازگشت",
	 "cht" => "返回",
	 "chb" => "返回"
);
if($exData[0] == "lang"){
	$langs[$id]=$exData[1];
	saveLangs ();
	$t=array(
		"ar" => "القائمة الرئيسية" ,
	 "en" => "Main Menu",
	 "ru" => "Главное меню",
	 "fa" => "منوی اصلی",
	 "cht" => "主菜單",
	 "chb" => "主菜单 "
	);
	edit("⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️",[[['text' => $t[$exData[1]],"callback_data" => "back"]]]);
}
if(!isset($langs[$id])){
	Lang:
	$tx = "
قم باختيار اللغة.
Please choose a language.
Пожалуйста, выберите язык.
 لطفاً زبان را انتخاب کنید.
 請選擇語言。
 请选擇语言。
	";
	$btn=[];
	foreach ($lang as $k=>$v) {
		$btn[]= array(
			"$v" => "lang#$k"
		);
	}
	if(isset($langs[$id])) $btn[]=array(
		$z[$langs[$id]] => "back"
	);
	if($text)
	send($tx, mkBtn ($btn));
	else
	edit($tx, mkBtn ($btn));
	exit;
}

$txt = $trans[$langs[$id]];
//send(json_encode($txt,448));
if(!check_member($id,$ch5)) {
	$link = "https://t.me/TG_FIREFOXBOT?start=0";
	$bt=[[['text' => "".$txt[1] ,"url"=>"$link"]]];
	$tx = $txt[2];
	if($text)
	send($tx,$bt);
	else
	edit ($tx,$bt);
	exit;
}
if($bans[$id] == $id) {
	$tx =$txt[3];
	send($tx);
	exit;
}
$a=array(
	 "ar" => "تغيير اللغة" ,
	 "en" => "Change Language",
	 "ru" => "Сменить язык",
	 "fa" => "تغییر زبان",
	 "cht" => "更改語言",
	 "chb" => "更改语言"
);
$back = mkBtn (array(
		array (
			$z[$langs[$id]]=> "back"
		)
	));
if($data == "back" ){
	goto A;
	B:
	edit($tx,$btn);
	exit;
}
if ($text == "/start" || $ex[0] == "/start") {
	if(!isset($points[$id] )){
		$points[$id]=0;
		if(isset($invite['whoInvitedMe'][$id])){
			$points[$invite['whoInvitedMe'][$id]]+=$invitePoint;
			$invite['invited'][$invite['whoInvitedMe'][$id]]=$id;
			saveInvite();
			$ty=$trans[$langs[$invite['whoInvitedMe'][$id]]];
			$tx = str_replace("__invitePoint__",$invitePoint,$ty[4]);
			send($tx,null,$invite['whoInvitedMe'][$id]);
		}
		savePoint ();	
	}
	A:
	$btn = mkBtn ([
		array(
			"{$txt[5]}" => "buy"
		),
		array(
			"{$txt[6]}" => "$requestLink",
			"{$txt[7]}" => "$supportLink"
		),
		array(
			"{$txt[8]}" => "wk",
			"{$txt[9]}" => "$ch4"
		),
		array(
			"{$txt[10]}" => "inviteLink"
		),
		array(
			"{$a[$langs[$id]]}" => "changeLange"
		)
	]);	
	$btn[2][1]['url']=$btn[2][1]['callback_data'];
	unset($btn[2][1]['callback_data']);
	$btn[1][0]['url']=$btn[1][0]['callback_data'];
	unset($btn[1][0]['callback_data']);
	$btn[1][1]['url']=$btn[1][1]['callback_data'];
	unset($btn[1][1]['callback_data']);
	$tx = $txt[11];
	if($data) goto B;
	send($tx,$btn);
} else if ($data == "requestPoint") {
	edit($txt[12],$back);
} else if ($data == "support") {
	edit($txt[13],$back);
}else if ($data == "changeLange"){
	goto Lang;
} else if ($data == "wk") {
	if (count($info['bot']['wk']) == 0) {
		$tx = $txt[14];
	} else {
		$tx = "{$txt[8]} \n\n";
		foreach ($info['bot']['wk'] as $k => $v ) {
			$k++;
			$tx .= "{$k} - {$v['name']} | {$v['user']} \n";
		}
	}
	edit($tx,$back);
} else if ($data == "inviteLink") {
	$tx = $txt[15];
	edit($tx,$back);
} else if ($data == "buy" || $exData[0] == 'next' || $exData[0] == 'before') {
	$tx=$txt[16];
	if ($data == "buy") {
		$start = 0;
	} else if ($exData[0] == 'next') {
		$start= $exData[1];
		if ($start > count ($contries)) {
			bot('answercallbackquery',[
				'callback_query_id'=>$update->callback_query->id,
				'show_alert'=>true,
				'text' => $txt[17],
			]);
			exit;
		}
	} else if ( $exData[0] == 'before') {
		$start= $exData[1];
		if($start >= 30) {$start -=30;}
		else if ($start > 0) { $start = 0;}
		else  {
			bot('answercallbackquery',[
				'callback_query_id'=>$update->callback_query->id,
				'show_alert'=>true,
				'text' => $txt[18],
			]);
			exit;
		}
	}
	
	$end = $start + 30;
	$btn =array();
	
	$tx=$txt[19];
	$bt=array();
	$count=-1;
	$a=0;
	foreach ($contries as $k => $p) {
		$count++;
		if($count < $start) continue;
		else if ($count >= $end) break;	
		/*$p = $prices[$k];
		$p = $p+($p*$revenue/100);*/
		if($a%2==0) {
			$btn[]=$bt;
			$bt=[];
			$bt[]=['text' => "{$tnames[$langs[$id]][$k]} | $p",'callback_data' => "getNum#$k"];
		} else {
			$bt[]=['text' => "{$tnames[$langs[$id]][$k]} | $p",'callback_data' => "getNum#$k" ];
		}
		$a++;
		//$tx .= "$k | {$names[$k]} | $p \n ";	
	}/*
	if($start >= 30){
		$b= $start -30;
	} else if ($start != 0) {
		$b = 0;
	} else {
		$b=-1;
	}*/
	if(count($bt)>0) $btn[]=$bt;
	$btn[]=array(
		['text' => "{$txt[20]}",'callback_data' => "before#{$start}" ],
		['text' => "{$txt[21]}",'callback_data' => "next#{$end}" ],
	);
	$btn[]=array(
	['text' => $z[$langs[$id]],'callback_data' => "back" ],
	);
	edit($tx,$btn);
} else if ($exData[0] == "getNum") {
	$btn = mkBtn (
		array(
			array(
				$txt[22] => "getNumber#" . $exData[1],
				$z[$langs[$id]] => "back"
			)
		)
	);
	$tx= $txt[23] . $tnames[$langs[$id]][$exData[1]];
	edit ($tx,$btn);
} else if ($exData[0] == "getNumber") {
	$p=$contries[$exData[1]]??0;
	if($p == 0 ) {
		bot('answercallbackquery',[
			'callback_query_id'=>$update->callback_query->id,
			'show_alert'=>true,
			'text' => $txt[24],
		]);
		exit;
	}
	/*$getPrices = $api->getCountries();
	if(!is_array($getPrices) ){
		bot('answercallbackquery',[
			'callback_query_id'=>$update->callback_query->id,
			'show_alert'=>true,
			'text' => "لا توجد ارقام لهذه الدولة في الوقت الحالي✖️"
		]);
		exit;
	}
	$p=-1;
	//send("$k | $exDate[1]");
	foreach ($getPrices as $k => $v){
		if($k == $exData[1]) {
			$p = $v;
			break;
		}
	}
	if($p == -1) {
		bot('answercallbackquery',[
			'callback_query_id'=>$update->callback_query->id,
			'show_alert'=>true,
			'text' => "لا توجد ارقام لهذه الدولة في الوقت الحالي❌"
		]);
	} else */if ($point >= $p) {
		$get = $api->getNumber($exData[1]);
		if (is_array($get)) {
			$num = $get['number'];
			$hashCode = $get['hash_code'];
			$c=$names[$exData[1]];
			$k=	$exData[1];
			$points[$id]-=$p;
			savePoint();
			$stats['all']['trybuy'] += 1;
			saveStats();
			//send message to channel ( $ch1)
			$tx = "
✅- تم شراء رقم من البوت بنجاح -✅

☎️ - الرقم: <code>$num</code>
🌎 - الدولة: $c
💢 - رمز الدولة: $k
💵- السعر :  $p$
💰 - الرصيد: $point
🆔 - الايدي: <code>$id</code>
";
			send($tx,null,$ch1);
			$tx = str_replace(["__c__","__num__","__p__"],
[$c,$num,$p],
$txt[25]);

			$btn = mkBtn (
				array(
					array (
						"{$txt[26]}" => "getCode#" . $hashCode . "#$k#$num"
					)
				)
			);
			edit($tx,$btn);
		} else {
			bot('answercallbackquery',[
			'callback_query_id'=>$update->callback_query->id,
			'show_alert'=>true,
			'text' => $txt[24]
		]);
		}
	} else {
		bot('answercallbackquery',[
			'callback_query_id'=>$update->callback_query->id,
			'show_alert'=>true,
			'text' => $txt[27],
		]);
	}
} else if ( $exData[0] == "getCode") {
	$hashCode = $exData[1];
	$get = $api->getCode($hashCode);
	if (is_array($get)) {
		$code = $get['code'];
		$pass = $get['password'];
		$stats['all']['buy'] += 1;
		$stats[$id]['buy'] += 1;
		saveStats();
		$c=$names[$exData[2]];
		$num = $exData[3];
               $p=$contries[$exData[2]]??0;
		$tx = str_replace(["__num__","__p__","__c__","__code__","__pass__"],
		[$num,$p,$c,$code,$pass],
 $txt[29]);
		edit($tx);		
		$tx = "
⚜️ تم وصول كود الرقم:

🌎 - الدولة: $c
☎️ - الرقم: <code>$num</code>
💰- السعر :  $p$
💬 - الكود : $code 🗯
🔑 - كلمة المرور: $pass
👤- المشتري : <code>$id</code>
🎗 - الموقع : السيرفر الرئيسي
";
		send($tx,null,$ch2);
		$idd = substr("$id",0,-4) . "••••";
		$num = substr("$num",0,-4) . "••••";
                $p=$contries[$exData[2]]??0;
		$tx = "
✅- تم شراء رقم من البوت بنجاح -✅

🌎 - الدولة: $c
📱 - حسابات تيليجرام جاهزة 📲

☎️ - الرقم: <tg-spoiler>$num</tg-spoiler> 📞
💰- السعر :  <tg-spoiler>$p$</tg-spoiler>  
💬 - الكود : $code 🗯
🆔- المشتري : <tg-spoiler>$idd</tg-spoiler>  👨🏻‍💻

☑️ - الحالة : تم التفعيل بنجاح ☑️
";
send($tx,[[["text" => "🤖 شراء رقم من البوت 🤖","url" => "https://t.me/يوزر قناة التفعيلات"]]],$ch3);
	} else {
		bot('answercallbackquery',[
			'callback_query_id'=>$update->callback_query->id,
			'show_alert'=>true,
			'text' => $txt[28],
		]);
	}	
}