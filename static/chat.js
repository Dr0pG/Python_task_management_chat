/*
    CHAT - Diogo Venãncio & André Gonçalves
*/

var chatClick = chatClick || $(document).on('click', 'i.project-chat', openChat);

$(document).on('click', 'i.chat-close', closeChat);

$(document).on('keyup', '.chat-input input', function (e) {
    if (e.keyCode != 13) {
        return;
    }

    sendMessage(e);
});

var searchLoop;

function loadMessages(projectId) {
    console.log("LOADING MESSAGES");
    let destination = $('.chat-messages');

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/chat/";
    req.open("GET", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            showMessages(destination, JSON.parse(this.responseText));
        }
    }
    req.send();
}

function sendMessage(e) {
    let msg = $(e.target).val();
    $(e.target).val("");
    if (msg == "") {
        return;
    }

    let projectId = localStorage.getItem("chat");
    console.log('sending message:' + msg);

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/chat/";
    req.open("POST", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            loadMessages(projectId);
        }
    }
    let params = JSON.stringify({
        project_id: projectId,
        content: msg
    });
    req.send(params);
}

function showMessages(destination, messages) {
    $(destination).empty();
    console.log(messages);
    $.each(messages, function (i, message) {
        let initial = message.username.charAt(0).toUpperCase();
        let owner;
        if (message.username == localStorage.getItem("username")) {
            owner = "owner";
        }
        $(destination).append(`
            <div class="message-row">
                <div id="collaborator-${message.sender}" title="${message.username}" class="collaborator">${initial}</div>
                <div class="message ${owner}">${message.content}</div>
            </div>
        `);
    });
}

function openChat(e) {
    closeChat(e);
    $('#chat').slideDown();
    let projectId = getProjectIdFromElement($(e.target));
    $('.chat-title').text($('#project-' + projectId + ' .project-name').text());
    localStorage.setItem("chat", projectId);

    searchLoop = window.setInterval(function () {
        loadMessages(projectId);
    }, 500);
}

function closeChat(e) {
    clearInterval(searchLoop);
    $('.chat-messages').empty();
    $('.chat-input input').val("");
    $('#chat').slideUp();
    localStorage.setItem("chat", -1);
}
