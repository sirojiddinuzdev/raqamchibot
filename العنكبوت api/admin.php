<?php 
$lang = json_decode(file_get_contents("langs.json"),1)??[];
$txt = array(
"ar" => array(
"1" => "✅ - تم إعادة شحن حسابك بـ مبلغ __point__",
"2" => "تم سحب __point__  من حسابك",
"3" => "تم حظرك من استخدام البوت",
"4"=> "تم الغاء حظرك من استخدام البوت",
),
"en" => array(
    "1" => "✅ - Your account has been recharged with __point__",
    "2" => "__point__ has been deducted from your account",
    "3" => "You have been banned from using the bot",
    "4" => "You have been unbanned from using the bot",
),
"ru" => array(
    "1" => "✅ - Ваш счет был пополнен на сумму __point__",
    "2" => "__point__ было списано с вашего счета",
    "3" => "Вы были забанены от использования бота",
    "4" => "Вы были разблокированы для использования бота",
),
"fa" => array(
    "1" => "✅ - حساب شما با مبلغ __point__ شارژ شد",
    "2" => "__point__ از حساب شما کسر شد",
    "3" => "شما از استفاده از ربات مسدود شده‌اید",
    "4" => "مسدودیت شما از استفاده از ربات لغو شد",
),
"cht" => array(
    "1" => "✅ - 您的帳戶已加值 __point__",
    "2" => "__point__ 已從您的帳戶中扣除",
    "3" => "您已被禁止使用機器人",
    "4" => "您已被解除禁止使用機器人",
),
"chb" => array(
    "1" => "✅ - 您的账户已充值 __point__",
    "2" => "__point__ 已从您的账户中扣除",
    "3" => "您已被禁止使用机器人",
    "4" => "您已被解除禁止使用机器人",
)
);
if ($text == "/start" || $data == "back") {
	$btn = 
	mkBtn(
		array(
			array(
				"اضافة رصيد" => "addPoint",
				"سحب رصيد" => "takePoint"
			),
			array(
				"حظر عضو" => "ban",
				"الغاء  الحظر" => "unban"
			),
			array(
				"اضافة وكيل" => "addWk",
				"حذف وكيل" => "remWk"
			),
			array(
				"الوكلاء" => "wk",
			),
			array(
				"اضافة دولة" => "addContry",
				"حذف دولة" => "remContry"
			),			
			array(
				"الاحصائيات" => "stats"
			)				
		)
	
	);
	$info[$id]['action']="";
	saveInfo();
	$tx = "اهلا وسهلا بك عزيزي الادمن\n رصيدك في موقع الارقام $balance\n\nاوامر الادمن";
	if ($text)
	send($tx,$btn);
	else
	edit($tx,$btn);
} else if ($data == "addPoint") {
	$tx = "قم بارسال ايدي العضو";
	$info[$id]['action']="addPointId";
	saveInfo();
	edit($tx,$back);
} else if ($text && ($info[$id]['action'] == "addPointId") ){
	echo "-@Ba_ageel-";
	if(!isset ($points[$text])) {
		//user not exist 
		$tx = "لا يوجد مستخدم بهذا الايدي";
		send($tx,$back);
	} else {
		$info[$id]['idPoint']  = $text;
		$info[$id]['action']="addPoint";
		saveInfo();
		$tx = "قم بارسال الرصيد الذي تريد اضافته";
		send($tx,$back);
	}
} else if ($text && $info[$id]['action'] == "addPoint") {
	if( is_numeric($text) && $text > 0 ) {
		$points[$info[$id]['idPoint']] += ($text);
		savePoint();
		$tx = "تم التحويل بنجاح";
		send($tx,$back);
		$tx=str_replace("__point__",$text,$txt[$lang[$info[$id]['idPoint']]][1]);
		send($tx,null,$info[$id]['idPoint']);
		$info[$id]['idPoint']  = "";
		$info[$id]['action']="";
		saveInfo();
	} else {
		$tx = "يجب ان ترسل رقم اكبر من الصفر";
		send($tx,$back);
	}
}else if ($data == "takePoint") {
	$tx = "قم بارسال ايدي العضو";
	$info[$id]['action']="takePointId";
	saveInfo();
	edit($tx,$back);
} else if ($text && ($info[$id]['action'] == "takePointId") ){
	echo "-@Ba_ageel-";
	if(!isset ($points[$text])) {
		//user not exist 
		$tx = "لا يوجد مستخدم بهذا الايدي";
		send($tx,$back);
	} else {
		$info[$id]['idPoint']  = $text;
		$info[$id]['action']="takePoint";
		saveInfo();
		$tx = "قم بارسال الرصيد الذي تريد سحبه من العضو";
		send($tx,$back);
	}
} else if ($text && $info[$id]['action'] == "takePoint") {
	if( is_numeric($text) && $text > 0 ) {
		$points[$info[$id]['idPoint']] -= ($text);
		savePoint();
		$tx = "تم السحب بنجاح";
		send($tx,$back);
		$tx=str_replace("__point__",$text,$txt[$lang[$info[$id]['idPoint']]][2]);
		send($tx,null,$info[$id]['idPoint']);
		$info[$id]['idPoint']  = "";
		$info[$id]['action']="";
		saveInfo();
	} else {
		$tx = "يجب ان ترسل رقم اكبر من الصفر";
		send($tx,$back);
	}
} else if ($data == "ban") {
	$tx = "قم بارسال ايدي العضو";
	$info[$id]['action']="ban";
	saveInfo();
	edit($tx,$back);
} else if ($text && $info[$id]['action'] == "ban") {
	$tx = "تم حظر العضو بنجاح";
	$info[$id]['action']="";
	saveInfo();
	$bans[$text]=$text;
	saveBans();
	send($tx,$back);
	$tx = $txt[$lang[$text]][3];
	send($tx,null,$text);
}else if ($data == "unban") {
	$tx = "قم بارسال ايدي العضو";
	$info[$id]['action']="unban";
	saveInfo();
	edit($tx,$back);
}else if ($text && $info[$id]['action'] == "unban") {
	$tx = "تم الغاء الحظر بنجاح";
	$info[$id]['action']="";
	saveInfo();
	$bans[$text]=null;
	saveBans();
	send($tx,$back);
	$tx = $txt[$lang[$text]][4];
	send($tx,null,$text);
} else if ($data == "addWk") {
	$tx = "قم بارسال الاسم في سطر واليوزر في السطر الثاني";
	$info[$id]['action']="addWk";
	saveInfo();
	edit($tx,$back);
} else if ($text && $info[$id]['action']=="addWk") {
	$extx = explode ("\n",$text);
	if(count ($extx) == 2) {
		$info['bot']['wk'] [] = array(
			"name" => $extx[0],
			"user" => $extx[1],
		);
		$info[$id]['action']="";
		saveInfo ();
		$tx="تمت اضافة الوكيل بنجاح";
		send($tx,$back);
	} else {
		$tx = "قم بارسال الاسم في سطر واليوزر في السطر الثاني";
		send($tx,$back);
	}
} else if ($data == "remWk" ) {
	$btn = array();
	$btn[]= 
		array(
			"الاسم" => "ntn",
			"اليوزر" => "ntn"
		);
	
	foreach ($info['bot']['wk'] as $k => $v ) {
		$d= "remWk-{$k}";
		$btn[] = 
			array(
				"{$v['name']}"??""=> $d,
				"{$v['user']}"??"" => $d,
			);
		
	}
	$btn[]=array (
			"رجوع" => "back"
		);
	$tx ="اختار الوكيل الذي تريد حذفة";
	edit($tx, mkBtn ($btn));
}else if (preg_match("/remWk\-/",$data)) {
	$info['bot']['wk'][explode ("-",$data)[1]]=null;
	unset($info['bot']['wk'][explode ("-",$data)[1]]);
	saveInfo ();
	$tx ="تم الحذف بنجاح";
	edit($tx, mkBtn ($btn));
} else if ($data == "wk") {
	$btn = array();
	$btn[]= 
		array(
			"الاسم" => "ntn",
			"اليوزر" => "ntn"
		);
	
	foreach ($info['bot']['wk'] as $k => $v ) {
		$btn[] = 
			array(
				"{$v['name']}"??""=> "ntn",
				"{$v['user']}"??"" => "ntn",
			);
	}
	$btn[]=array (
			"رجوع" => "back"
		);
	$tx ="جميع الوكلاء";
	edit($tx, mkBtn ($btn));
} else if ($data == "addContry" || $exData[0] == 'next' || $exData[0] == 'before') {
	#Lista:
	$get = $api->getCountries();
	$tx="الدول المتاحة\n";
	if ($data == "addContry" ) {
		$start = 0;
	} else if ($exData[0] == 'next') {
		$start= $exData[1];
		if ($start > count ($get)) {
			bot('answercallbackquery',[
				'callback_query_id'=>$update->callback_query->id,
				'show_alert'=>true,
				'text' => "لا توجد قائمة تاليه"
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
				'text' => "لا توجد قائمة سابقة"
			]);
			exit;
		}
	}	
	$end = $start + 30;
	$btn =array();
	$bt=array();
	$count=-1;
	$a=1;
	$btn[]=[['text' => "الدولة | الكلفة",'callback_data' => "test" ],['text' => "الدولة | الكلفة ",'callback_data' => "change#$z"]];
	foreach ($get as $k => $p) {
		$count++;
		if($count < $start) continue;
		else if ($count >= $end) break;
		$z = isset($contries[$k])? "✅" : "❌";
		//$btn[]=[['text' => "{$names[$k]} | $p",'callback_data' => "change#$k#$data" ],['text' => "$z",'callback_data' => "change#$k#$data"]];
		if($a%2==0) {
			$bt[]=['text' => "{$names[$k]} | $p",'callback_data' => "add#$k#$data" ];
			$btn[]=$bt;
			$bt=[];
		} else {
			$bt[]=['text' => "{$names[$k]} | $p",'callback_data' => "add#$k#$data" ];
		}
		$a++;
	}
	if(count($bt)>0) $btn[]=$bt;
	$btn[]=array(
		['text' => "السابق ⏮️",'callback_data' => "before#{$start}" ],
		['text' => "⏭️التالي ",'callback_data' => "next#{$end}" ],
	);
	$btn[]=array(
		['text' =>" رجوع 🔙",'callback_data' => "back" ],
	);
	
	edit($tx,$btn);
} /*else if ($exData[0] == "change") {
	if ( !isset($contries[$exData[1]])) {
		$contries[$exData[1]]=$exData[1];
	} else {
		unset($contries[$exData[1]]);
	}
	saveContries ();
	unset($exData[1]);
	unset($exData[0]);
	$data = implode ("#",$exData);
	$exData=explode ("#",$data);
	goto Lista;
}*/ else if ($data == "stats") {
	$a=$stats['all']['trybuy']??0;
	$b= $stats['all']['buy']??0;
	$tx = "عدد عمليات الشراء $a\nعدد العمليات الناجحة$b";
	edit ($tx,$back);
} else if ($exData[0] == "add") {
	$info[$id]['action']="addContry";
	$info[$id]['contry']=$exData[1];
	saveInfo();
	$tx = "قم بارسال سعر البيع";
	$btn =mkBtn (
		array(
			"رجوع🔙" => $exData[2]
		)
	);
	edit($tx,$btn);
} else if ($text && $info[$id]['action']=="addContry") {
	if ( is_numeric($text) && $text > 0 ) {
		$tx = "تمت اضافة الدولة بنجاح";
		$contries[$info[$id]['contry']]=$text;
		$info[$id]['action']="";
		$info[$id]['contry']="";
		saveInfo();
		saveContries ();
	} else {
		$tx="قم بارسال قيمة رقمية اكبر من الصفر";
	}
	send($tx,$back);
} else if ($data == "remContry" || $exData[0] == 'NEXT' || $exData[0] == 'BEFORE') {
	$tx="الدول المتاحة\n";
	if ($data == "remContry") {
		$start = 0;
	} else if ($exData[0] == 'NEXT') {
		$start= $exData[1];
		if ($start > count ($contries)) {
			bot('answercallbackquery',[
				'callback_query_id'=>$update->callback_query->id,
				'show_alert'=>true,
				'text' => "لا توجد قائمة تاليه"
			]);
			exit;
		}
	} else if ( $exData[0] == 'BEFORE') {
		$start= $exData[1];
		if($start >= 30) {$start -=30;}
		else if ($start > 0) { $start = 0;}
		else  {
			bot('answercallbackquery',[
				'callback_query_id'=>$update->callback_query->id,
				'show_alert'=>true,
				'text' => "لا توجد قائمة سابقة"
			]);
			exit;
		}
	}	
	$end = $start + 30;
	$btn =array();
	
	$tx="
	قم باختيار الدولة التي تريد خذفها
	";
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
			$bt[]=['text' => "{$names[$k]} | $p",'callback_data' => "remove#$k"];
		} else {
			$bt[]=['text' => "{$names[$k]} | $p",'callback_data' => "remove#$k" ];
		}
		$a++;
		//$tx .= "$k | {$names[$k]} | $p \n ";	
	}
	if(count($bt)>0) $btn[]=$bt;
	$btn[]=array(
		['text' => "السابق ⏮️",'callback_data' => "BEFORE#{$start}" ],
		['text' => "⏭️التالي ",'callback_data' => "NEXT#{$end}" ],
	);
	$btn[]=array(
	['text' => "رجوع 🔙",'callback_data' => "back" ],
	);
	edit($tx,$btn);
} else if ($exData[0] == "remove") {
	//send($exData[1]);
	$contries[$exData[1]]=null;
	unset($contries[$exData[1]]);
	saveContries ();
	//send(json_encode($contries));
	$tx="تم الحذف بنجاح";
	edit($tx,$back);
}
