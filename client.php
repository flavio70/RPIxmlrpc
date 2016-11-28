<!DOCTYPE html>
<html>
<body>

<h1>XML RPC Client example</h1>
<h2>python server and php Client</h2>


<?php
//XML RPC Client example

require_once __DIR__.'/vendor/autoload.php';



PhpXmlRpc\Autoloader::register();

$client = new PhpXmlRpc\Client("http://151.98.64.32:8080");



$client->return_type = 'phpvals'; // let client give us back php values instead of xmlrpcvals

//$client->return_type = 'xml';


//Getting pin status value using GET Method
$pin_status=$_GET['pin_status'];



function callRPC($client,$message,$pars) {


	$resp = $client->send(new PhpXmlRpc\Request($message,$pars));

	if ($resp->faultCode()) {
    		echo "<h3>Server method " . $message . " could not be retrieved: error {$resp->faultCode()} '" . htmlspecialchars($resp->faultString()) . "'</h3>\n";
	} else {
    		echo "<h3>Server method " . $message . "  retrieved, now wrapping it up...</h3>\n\n";
    		flush();
	}

	$struct = $resp->value();
	echo "<h4>Value returned by server: '" . $struct . "'</h4>";
	return $struct;

}




//input array for setGPIO remote call
$inAr = array("2" => $pin_status);
// create parameters from the input array: an xmlrpc array of xmlrpc structs
$p = array();
foreach ($inAr as $key => $val) {
    $p[] = new PhpXmlRpc\Value(
        array(
            "gpio" => new PhpXmlRpc\Value($key),
            "status" => new PhpXmlRpc\Value($val)
        ),
        "struct"
    );
}
$v = new PhpXmlRpc\Value($p, "array");
//print "Encoded into xmlrpc format it looks like this: <pre>\n" . htmlentities($v->serialize()) . "</pre>\n";




$res = callRPC($client,'checkServer'); // no input for this procedure
$res = callRPC($client,'setGPIO',array($v));



echo "<p>decoded json vars:</p>\n";

$obj = json_decode($res);


echo "\n<p>Pin: " . $obj->{'gpio'} . "</p>";;
echo "\n<p>Status: " . $obj->{'status'} . "</p>";

?>

</body>
</html>

