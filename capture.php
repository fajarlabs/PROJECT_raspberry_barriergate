<?php 
// ffmpeg -y -i "rtsp://192.168.0.77:554/mpeg4?username=admin&password=E10ADC3949BA59ABBE56E057F20F883E" -vframes 1 do.jpg
$ip = '192.168.0.77';
$username = 'admin';
$password = 'E10ADC3949BA59ABBE56E057F20F883E';
$save_directory = "C:\\xampp\\htdocs\\parkir\\";
$file_name = "do.jpeg";

function capture_cctv($ip, $username, $password, $save_directory, $file_name) {
	system("ffmpeg -y -i \"rtsp://$ip:554/mpeg4?username=$username&password=$password\" -vframes 1 ".$save_directory.$file_name, $retval);
	return $retval; // 0 is success, 1 is failed
}

// how to used
print_r(capture_cctv($ip, $username, $password, $save_directory, $file_name));

?>
