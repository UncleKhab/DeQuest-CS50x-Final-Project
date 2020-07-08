function checkform(theForm, theButton)
        {
            let logform= document.forms[theForm].elements;
            let cansubmit = true;
            let length = logform.length;
            for(let i = 0; i< length; i++)
            {
                if(logform[i].value.length == 0) cansubmit = false;
            }

               document.getElementById(theButton).disabled = !cansubmit;
        }

function displayAlert(message){
            document.querySelector("#displayAlert").innerText = message;
            document.querySelector("#displayAlert").style.display = "block"
            setTimeout(function(){ document.querySelector("#displayAlert").style.display = "none"; }, 3000);
        }