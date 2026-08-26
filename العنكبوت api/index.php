<?php

//    
//error_reporting(E_ERROR);
	
require_once "vals.php";
require_once "contries.php";
require_once "api.php";
define('API_KEY', $token);
#functions 
function bot($method, $datas = [])
{
    $url = "https://api.telegram.org/bot" . API_KEY . "/" . $method;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $datas);
    $res = curl_exec($ch);
    file_put_contents('error.txt', json_encode(json_decode($res),448)."\n$method".__LINE__, FILE_APPEND);
    
    if (curl_error($ch)) {
        //var_dump(curl_error($ch));
        $res = json_decode($res);
        
        return $res;
    } else {
        $res = json_decode($res);
        #file_get_contents("https://api.telegram.org/bot" . API_KEY . "/sendmessage?chat_id=501030516&text=" . urlencode(json_encode($res,448)."\n$method".__LINE__));
        return $res;
    }
}
$link =  "https://".$_SERVER["SERVER_NAME"].$_SERVER["PHP_SELF"];
echo file_get_contents("https://api.telegram.org/bot$token/setWebHook?url=$link");
function check_member($id, $chat){
    $join = bot('getChatMember', ["chat_id" => $chat, "user_id" => $id])->result->status;
    if($join == 'left' or $join == 'kicked'){
        return false;
    }else{
        return true;
    }
}
/*
array(
	array(
	text => data,
	text => data
	),
	array(
	text => data,
	)
)
*/

//one line button 
function mkBtn($btn) {
	$res = array();
	foreach ($btn as  $d) {
		$r = array();
		foreach ($d as $k => $v ) {
			$r[] = ['text' => $k , 'callback_data' => $v];
		}
		$res[] = $r;
	}
	return $res;
}

function send($text,$btn=null,$id=null) {
	if ($id == null) {
		global $id;
	}
	$data = array();
	$data['chat_id'] = $id;
	$data['text'] = $text;
	$data['parse_mode'] ='html';
	if($btn != null){
		$data['reply_markup'] = json_encode([
			'inline_keyboard' => $btn
		]);
	}
	return bot('sendMessage',
		$data
	);
}
function edit ($text,$btn=null){
	$data = array();
	global $id;
	global $message_id;
	$data['chat_id'] = $id;
	$data['text'] = $text;
	$data['parse_mode'] ='html';
	$data['message_id']=$message_id;
	if($btn != null){
		$data['reply_markup'] = json_encode([
			'inline_keyboard' => $btn
		]);
	}
	return bot('editMessageText',
		$data
	);
}
function savePoint() {
	global $points;
	if($points != null) {
		file_put_contents("points.json",json_encode($points,448));
	}
}
function saveStats() {
	global $stats;
	if($stats != null) {
		file_put_contents("stats.json",json_encode($stats,448));
	}
}
function saveOp() {
	global $op;
	if($op != null) {
		file_put_contents("operations.json",json_encode($op,448));
	}
}
function saveInvite() {
	global $invite;
	if($invite != null) {
		file_put_contents("invites.json",json_encode($invite,448));
	}
}
function saveBans() {
	global $bans;
	if($bans != null) {
		file_put_contents("bans.json",json_encode($bans,448));
	}
}
function saveInfo() {
	global $info;
	if($info != null) {
		file_put_contents("info.json",json_encode($info,448));
	}
} 
function saveContries() {
	global $contries;
	if($contries != null) {
		file_put_contents("contries.json",json_encode($contries,448));
	}
}

$back = mkBtn (array(
		array (
			"رجوع" => "back"
		)
	));
#end functions
$update = json_decode(file_get_contents('php://input'));
if ($update->message) {
    $message = $update->message;
    $chat_id = $message->chat->id;
    $text = $message->text;
    $ex = explode(" ", $text);
    $first_name = $update->message->from->first_name;
    $username = $message->from->username;
    $id = $message->from->id;
    $message_id = $message->message_id;
    $entities = $message->entities;
    $language_code = $message->from->language_code;
    $tc = $update->message->chat->type;
    $re_message = $update->message->reply_to_message;
    $re_text = $re_message->text;
} else if ($update->callback_query) {
    $chat_id = $update->callback_query->message->chat->id;
    $id = $update->callback_query->from->id;
    $first_name = $update->callback_query->from->first_name;
    $message_id = $update->callback_query->message->message_id;
    $data = $update->callback_query->data;   
	$exData=explode ("#",$data); 
} else {
	exit;
}
#points {id,points}
$points = json_decode(file_get_contents("points.json"),1);
$point = $points[$id]??0;

#stats {sell  ,success ,all_points, price_sold_nums}}
$stats = json_decode(file_get_contents("stats.json"),1)??[];
#operations {id_op {time,buyer_id, county, number,code,price}}
$op = json_decode(file_get_contents("operations.json"),1)??[];
#invites | whoInvitedMe {id ,who send link} , invited{id,who use my link}
$invite = json_decode(file_get_contents("invites.json"),1)??[];
#bans
$bans = json_decode(file_get_contents("bans.json"),1)??[];
#--
$info = json_decode(file_get_contents("info.json"),1)??[];
#--
$contries = json_decode(file_get_contents("contries.json"),1)??[];
#--
$api = new Api($api_key);
if ($id == $admin) {
	$balance = $api->getBalance()??0; //api balance for admin
	require "admin.php";
} else {
	require "member.php";
}



