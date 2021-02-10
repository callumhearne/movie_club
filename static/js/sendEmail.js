  
function sendMail(contactForm) {
    emailjs.send("gmail", "film_club", {
        "from_name": contactForm.username.value,
        "from_email": contactForm.emailaddress.value,
    })
}