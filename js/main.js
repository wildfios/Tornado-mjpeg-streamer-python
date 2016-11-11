$(document).ready(function(){

    function chres(w, h){
        var data = new FormData();
        data.append('width', w);
        data.append('height', h);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/setparams', true);
        xhr.send(data);
    }

    $("#low").click(function(){
        chres(100, 100);
	})

	$("#norm").click(function(){
        chres(320, 240);
	})

	$("#hi").click(function(){
        chres(800, 600);
	})
});