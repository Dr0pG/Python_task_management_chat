/**
 * REST Client - Diogo Venâncio & André Gonçalves
 */

function login() {
    let username = $('.form-login input[name=username]').val();
    let password = $('.form-login input[name=password]').val();

    if (!username || !password) {
        alert("All fields are required");
        return;
    }
    var req = new XMLHttpRequest();
    req.open("POST", "/api/user/login/");

    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status === 200) {
                localStorage.setItem("username", username);
                showMenu();
                $('#container').load("/static/projects.html");
            } else if (this.status === 403) {
                alert("Incorrect Credentials!");
            }
        }
    }
    let params = JSON.stringify({
        username: username,
        password: password
    });

    req.send(params);
}

function register() {
    let email = $('.form-register input[name=email]').val();
    let username = $('.form-register input[name=username]').val();
    let password = $('.form-register input[name=password]').val();
    let confirmPassword = $('.form-register input[name=confirm_password]').val();

    if (password != confirmPassword) {
        alert("Passwords don't match");
        return;
    }

    if (!email || !username || !password) {
        alert("All fields are required");
        return;
    }

    var req = new XMLHttpRequest();
    req.open("POST", "/api/user/register/");
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 201) {
            $('.form-register input').val("");
            alert("Welcome to TaskList!");
        }
    }

    let params = JSON.stringify({
        username: username,
        email: email,
        password: password
    });
    req.send(params);
}

function logout() {
    var req = new XMLHttpRequest();
    req.open("GET", "/api/user/logout/");
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            localStorage.setItem("username", -1);
            hideMenu();
            location.reload();
        }
    }
    req.send();
}

function openAccount() {
    $('#container').load("/static/account.html");
}

function openProjects() {
    $('#container').load("/static/projects.html");
}

function showMenu() {
    $('.menu').append(`
        <li class="logout">Log out</li>
        <li class="projects">Projects</li>
        <li class="account">Account</li>
    `)
}

function hideMenu() {
    $('.menu').empty();
}

