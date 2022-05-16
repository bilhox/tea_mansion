var i = 0,text;
text = "The tea mansion"

function typing(){
    if(i<text.length){
        document.getElementById("text").innerHTML += text.charAt(i);
        i++;
        setTimeout(typing,200);
    
    }
}
typing();















