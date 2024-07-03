// window.onload = function() {
//     const random_pool = document.getElementById("random-pool");
//     const random_button = document.getElementById("random-button");
//     const random_result = document.getElementById("random-result");
//     const information_button = document.getElementById("information-button");
//     random_button.onclick = function() {
//         let names = random_pool.value.split(' ');
//         const time = new Date().getTime();
//         let name = names[time%names.length];
//         random_result.innerText = name;
//     }
//     information_button.onclick = function(){
//         alert(`声明：
//         1.抽取的人都是七年级下学期第二次月考考90~110分的人（包含两个边界值）
//         2.此程序基于JavaScript获取时间戳函数进行的随机抽取，无任何暗箱操作
//         3.JavaScript的时间戳每毫秒更新一次，就是说当1ms能运行该程序2次（1s运行2000次）时，是可以抽到同一个人的
//         4.抽取到的人请自觉交出作业，否则将会对该人加权`)
//     }
// }
window.alert = function(str){
    var shield = document.createElement("DIV");
    shield.id = "shield";
    shield.style.position = "absolute";
    shield.style.left = "0px";
    shield.style.top = "0px";
    shield.style.width = "100%";
    shield.style.height = "100%";
    //弹出对话框时的背景颜色
    shield.style.background = "#fff";
    shield.style.textAlign = "center";
    shield.style.zIndex = "25";
    //背景透明 IE有效
    //shield.style.filter = "alpha(opacity=0)";
    var alertFram = document.createElement("DIV");
    alertFram.id="alertFram";
    alertFram.style.position = "relative";
    alertFram.style.margin = "auto";
    alertFram.style.width = "50%";
    alertFram.style.height = "150px";
    alertFram.style.background = "#ff0000";
    alertFram.style.minWidth = "500px";
    // alertFram.style.textAlign = "center";
    alertFram.style.lineHeight = "150px";
    alertFram.style.zIndex = "300";
    alertFram.style.transform = "translate(0px, -400px)";
    strHtml = "<ul style=\"list-style:none;margin:0px;padding:0px;width:100%;\">\n";
    strHtml += " <li style=\"background:#DD828D;text-align:left;padding-left:20px;font-size:25px;font-weight:bold;height:40px;line-height:40px;border:1px solid #F9CADE;\">声明</li>\n";
    strHtml += " <li style=\"background:#fff;font-size:24px;height:250px;line-height:30px;border-left:1px solid #F9CADE;border-right:1px solid #F9CADE;\"><div>"+str+"</div></li>\n";
    strHtml += " <li style=\"background:#FDEEF4;text-align:center;font-weight:bold;height:25px;line-height:25px; border:1px solid #F9CADE;\"><input type=\"button\" value=\"确 定\" onclick=\"doOk()\" /></li>\n";
    strHtml += "</ul>\n";
    alertFram.innerHTML = strHtml;
    document.body.appendChild(alertFram);
    document.body.appendChild(shield);
    this.doOk = function(){
        alertFram.style.display = "none";
        shield.style.display = "none";
    }
    alertFram.focus();
    document.body.onselectstart = function(){return false;};
}
window.onload = function() {
    const random_pool = document.getElementById("random-pool");
    const random_button = document.getElementById("random-button");
    const random_result = document.getElementById("random-result");
    const information_button = document.getElementById("information-button");
    random_button.onclick = function() {
        let names = random_pool.value.split(' ');
        const time = new Date().getTime();
        let name = names[time%names.length];
        random_result.innerText = name;
    }
    information_button.onclick = function(){
        alert("\n1.抽取的人都是七年级下学期第二次月考考90~110分的人（包含两个边界值）\n2.此程序基于JavaScript获取时间戳函数进行的随机抽取，无任何暗箱操作\n3.JavaScript的时间戳每毫秒更新一次，就是说当1ms能运行该程序2次（1s运行2000次）时，是可以抽到同一个人的\n4.抽取到的人请自觉交出作业，否则将会对该人加权")
    }
}