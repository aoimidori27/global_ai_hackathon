function submit() {
	var jsonString = document.getElementById("myJson").value;
	//console.log(jsonString);
	var jsonObj = JSON.parse(jsonString);
	//console.log(jsonObj);

	var request = new XMLHttpRequest();
	var url = 'http://localhost:8010';
   	request.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200) {
            console.log ("success");
        }
	    else if (this.readyState == XMLHttpRequest.DONE) {
        	//console.log(request);
			doSomethingLoop(1, 0);
    	}
    }

    request.open('POST', url, true);
	request.setRequestHeader('content-type',
  	'		application/x-www-form-urlencoded;charset=UTF-8');
	request.withCredentials = true;
	//console.log(JSON.stringify(jsonString));
    request.send( JSON.stringify(jsonString) );
}

function doSomethingLoop(maxCount, i) {
  if (i <= maxCount) {
    setTimeout(function(){doSomethingLoop(maxCount, ++i)}, 1000);
	show(); // FIXME don't load local output
  }
}

function show() {
	var fileName = "data/sample.json";
	var request = new XMLHttpRequest();

	document.getElementById("myAlgorithm").innerHTML = "";
	document.getElementById("myKeyword").innerHTML = "";
	document.getElementById("myIssue").innerHTML = "";

	request.open('GET', fileName, true);
	request.responseType = 'text';
	request.send();

	request.onload = function() {
	  	var text = request.response;
	  	var data = JSON.parse(text);
		console.log(data);
		showAlgorithmHtml(data.algorithm);
		showIssueHtml(data.issue);
		showKeywordHtml(data.keyword);
	}
}

function init() {
}

function showAlgorithmHtml(alg) {
	document.getElementById("myAlgorithm").innerHTML = alg;
}
function showIssueHtml(issue) {
	for (var i in issue) {
		addLiElm("myIssue", issue[i]);
	}
}
function showKeywordHtml(word) {
	for (var i in word) {
		addLiElm("myKeyword", word[i]);
	}
}

function addLiElm(idname, txt) {
	//console.log(txt);
    var elm = document.getElementById(idname);
    var li = document.createElement("li");
    var text = document.createTextNode(txt);
    li.appendChild(text);
    elm.appendChild(li);
}
