const registerform = document.querySelector("#registerform");

function logSubmit(event) {
    event.preventDefault();

    emailjs.send("gmail", "film_club", {
        "from_name": registerform.username.value,
        "from_email": registerform.emailaddress.value
    })

    registerform.submit();
    registerform.requestFullscreen();

}

registerform.addEventListener('submit', logSubmit);