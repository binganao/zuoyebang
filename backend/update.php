<?php

header('Content-Type:application/json; charset=utf-8');

if($_SERVER['REQUEST_METHOD'] == 'POST'){
    $version = array('code'=>"200",'version'=>"1.12.5",'message'=>"欢迎使用饼干抢题工具\n饼干の博客：https://bingbingzi.cn\n暑假期间题池题目数量少，请耐心等待抢题\n「使用本脚本造成的一切后果本人概不负责」\n天气炎热，饼干提醒各位多喝水！！！",'upload_message'=>"新版本：1.12.5 已发布，更新内容：\n- 修复代码BUG\n- 增加抢题间隔选项\n- 修改抢题阈值，使网络效率更高\n- 提高抢题成功率\n- 增加对配置文件的说明\n- 增加更新API的支持，不用再依赖百度网盘了\n- 增加对Ctrl+C的错误处理\n\n本次更新还需要前往饼干博客获取更新：https://bingbingzi.cn");
}
else{
    $version = array('code'=>"201",'message'=>"不要来看api啊！！");
}
$info = str_replace("\\/", "/", json_encode($version));

exit($info);

?>