window.alert = function (title, str) {
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
    alertFram.id = "alertFram";
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
    strHtml += " <li style=\"background:#DD828D;text-align:left;padding-left:20px;font-size:25px;font-weight:bold;height:40px;line-height:40px;border:1px solid #F9CADE;\">" + title + "</li>\n";
    strHtml += " <li style=\"background:#fff;font-size:24px;height:250px;line-height:30px;border-left:1px solid #F9CADE;border-right:1px solid #F9CADE;\"><div>" + str + "</div></li>\n";
    strHtml += " <li style=\"background:#FDEEF4;text-align:center;font-weight:bold;height:25px;line-height:25px; border:1px solid #F9CADE;\"><input type=\"button\" value=\"确 定\" onclick=\"doOk()\" /></li>\n";
    strHtml += "</ul>\n";
    alertFram.innerHTML = strHtml;
    document.body.appendChild(alertFram);
    document.body.appendChild(shield);
    this.doOk = function () {
        alertFram.style.display = "none";
        shield.style.display = "none";
    }
    alertFram.focus();
    document.body.onselectstart = function () { return false; };
}
window.onload = function () {
    if (localStorage.getItem("1") !== "true") {
        alert("提示", "声明已更新");
    }
    var video = document.getElementById('video');
    document.getElementsByTagName("body")[0].appendChild(video);
    video.addEventListener('ended', function () {
        video.style.display = "none";
    });
    const random_pool = document.getElementById("random-pool");
    const random_button = document.getElementById("random-button");
    const random_result = document.getElementById("random-result");
    const information_button = document.getElementById("information-button");
    random_button.onclick = function () {
        let names = random_pool.value.split(' ');
        const time = new Date().getTime();
        if (time%2 == 0) {
            video.src = "https://cn-zjjh-ct-04-36.bilivideo.com/upgcxcode/78/54/1129605478/1129605478-1-16.mp4?e=ig8euxZM2rNcNbRVhwdVhwdlhWdVhwdVhoNvNC8BqJIzNbfq9rVEuxTEnE8L5F6VnEsSTx0vkX8fqJeYTj_lta53NCM=&uipk=5&nbs=1&deadline=1720695991&gen=playurlv2&os=bcache&oi=1857409762&trid=0000c6226c0ad2e2423e8c221328a132bc22h&mid=1077212711&platform=html5&og=cos&upsig=2b4eb83cf5a5c13b59462eaa42b1a6bc&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&cdnid=65864&bvc=vod&nettype=0&f=h_0_0&bw=50817&logo=80000000";
            video.style.display = "block";
            video.play();
        } else if (time%2 == 1) {
            video.src = "https://cn-hljheb-ct-01-04.bilivideo.com/upgcxcode/26/23/484282326/484282326-1-16.mp4?e=ig8euxZM2rNcNbRVhwdVhwdlhWdVhwdVhoNvNC8BqJIzNbfq9rVEuxTEnE8L5F6VnEsSTx0vkX8fqJeYTj_lta53NCM=&uipk=5&nbs=1&deadline=1720695385&gen=playurlv2&os=bcache&oi=1857409762&trid=0000fa0fa67285b54d8ca3397c53bc2fad3bh&mid=1077212711&platform=html5&og=cos&upsig=a308d6af1632d2d1091b4fd42ef73512&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&cdnid=3843&bvc=vod&nettype=0&f=h_0_0&bw=54377&logo=80000000";
            video.style.display = "block";
            video.play();
        }
        setTimeout(()=>{
            let name = names[time % names.length];
            random_result.innerText = name;
        },400)
    }
    information_button.onclick = function () {
        alert("声明", "1.抽取的人都是七年级下学期第二次月考考90~110分的人（包含两个边界值） 2.此程序基于JavaScript获取时间戳函数进行的随机抽取，无任何暗箱操作 3.JavaScript的时间戳每毫秒更新一次，就是说当1ms能运行该程序2次（1s运行2000次）时，是可以抽到同一个人的 4.抽取到的人请自觉交出作业，否则将会对该人加权并对该人所在的小组扣一分");
        localStorage.setItem("1", "true");
    }
}