<?php 

class Api {
	//public $api_key;
	public $url = "https://api.spider-service.com?apiKay=";
	public function __construct($api_key) {
		$this->url .= $api_key;
	}
	public function getData($data){
		$url = $this->url;
		foreach ($data as $k => $v ) {
			$url .= "&{$k}={$v}";
		}
		return json_decode(file_get_contents($url),1);
	}
	public function getBalance () {
		$getData = $this->getData(
			array(
				"action" => "getBalance"
			)
		);
		if ($getData['error'] == 'INFORMATION_SUCCESS') {
			return $getData['result']['wallet'];
		} else {
			 return 0 ;
		}
	}
	public function getNumber($countryCode) {
		$getData = $this->getData(
			array(
				"action" => "getNumber",
				"country" => $countryCode
			)
		);
		if ($getData['error'] == 'INFORMATION_SUCCESS') {
			return array(
				'number' => $getData['result']['phone'],
				'hash_code' => $getData['result']['hash_code'],
			);
		} else {
			 return "error" ;
		}
	}
	public function getCode($hashCode) {
		$getData = $this->getData(
			array(
				"action" => "getCode",
				"hash_code" => $hashCode
			)
		);
		if ($getData['error'] == 'INFORMATION_SUCCESS') {
			return $getData['result'];
		} else {
			 return "error" ;
		}
	}
	public function getCountries() {
		$getData = $this->getData(
			array(
				"action" => "getCountrys",
			)
		);
		if ($getData['error'] == 'INFORMATION_SUCCESS') {
			return $getData['result']['countries'][1];
		} else {
			 return "error" ;
		}
	}
}