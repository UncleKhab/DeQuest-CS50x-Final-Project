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

function submitCheck(theForm)
        {
            let qForm = document.forms[theForm].elements;
            
            for(let i = 1; i < 8; i += 2)
                {
                    if (qForm[i].checked == true)
                    {
                        return true;
                    }
                }

            event.preventDefault();
            alert("Plase Select One Correct Answer");
            return false;
        }
