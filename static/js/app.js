let currentRecipient = '';
let chatInput = $('#chat-input');
let chatButton = $('#btn-send');
let userList = $('#user-list');
let messageList = $('#messages');

function updateUserList() {
    $.getJSON('api/v1/user/', function (data) {
        userList.children('.user').remove();
        for (let i = 0; i < data.length; i++) {
	    let btn_class = "btn btn-danger btn-sm"
	    if(data[i]['online']){
		btn_class = "btn btn-success btn-sm"
	    }
            const userItem = `<a class="list-group-item user" data-username="${data[i]['id']}">${data[i]['username']}
		  <button
	    type="button"
	    id="user_${data[i]['id']}"
	    class="${btn_class}"
	    style="float:right;">offline</button>
		</a>`;
            $(userItem).appendTo('#user-list');
        }
        $('.user').click(function () {
            userList.children('.active').removeClass('active');
            let selected = event.target;
            $(selected).addClass('active');
            setCurrentRecipient(selected.getAttribute("data-username"));
        });
    });
}

function drawMessage(message) {
    // draw the messages in the forntend
    // using JS
    
    let position = 'left';
    const date = new Date(message.timestamp);
    if (message.user === currentUser) position = 'right';
    const messageItem = `
            <li class="message ${position}">
                <div class="avatar">${message.user}</div>
                    <div class="text_wrapper">
                        <div class="text">${message.body}<br>
                            <span class="small">${date}</span>
                    </div>
                </div>
            </li>`;
    $(messageItem).appendTo('#messages');
}

function getConversation(recipient) {
    // message used to get the last messages
    // of the user in the conversation. it depends
    // upon the settings file's MESSAGES_TO_LOAD variable
    // by default it is 15. it means only last 15 messages will be displayed
    
    $.getJSON(`/api/v1/message/?target=${recipient}`, function (data) {
        messageList.children('.message').remove();
        for (let i = data['results'].length - 1; i >= 0; i--) {
            drawMessage(data['results'][i]);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });

}

function getMessageById(message_id) {
    // funcition used to fetch the message
    // from the backend databaes using an ID
    // which is received using webhook.
    id = message_id
    $.getJSON(`/api/v1/message/${id}/`, function (data) {
        if (data.user === currentRecipient ||
            (data.recipient === currentRecipient && data.user == currentUser)) {
            drawMessage(data);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });
}

function sendMessage(recipient, body) {
    // funciton used to send
    // message to the database using post
    // request.
    $.post('/api/v1/message/', {
        recipient: recipient,
        body: body
    }).fail(function () {
        alert('Error! Check console!');
    });
}

function setCurrentRecipient(username) {
    currentRecipient = username;
    getConversation(currentRecipient);
    enableInput();
}


function enableInput() {
    chatInput.prop('disabled', false);
    chatButton.prop('disabled', false);
    chatInput.focus();
}

function disableInput() {
    chatInput.prop('disabled', true);
    chatButton.prop('disabled', true);
}

function updateOnlineOfflineStatus(user_id, status){
    if(status == "online"){
	try{
	    let user_anchor_element = document.getElementById(`user_${user_id}`)
	    
	}
	catch(e){
	}
    }
}
$(document).ready(function () {
    updateUserList();
    disableInput();

    var socket = new WebSocket(
        'ws://' + window.location.host +
        `/ws?session_key=${sessionKey}`)

    chatInput.keypress(function (e) {
        if (e.keyCode == 13)
            chatButton.click();
    });

    chatButton.click(function () {
	// when ever send button is clicked
	// if the user have typed anyting with
	// length > 0 we will send it. otherwise
	// noting will happend at all.
        if (chatInput.val().length > 0) {
            sendMessage(currentRecipient, chatInput.val());
            chatInput.val('');
        }
    });

    socket.onmessage = function (e) {
	// we receive the ID of the message
	// using socket. after that we will call
	// the API to fetch the content of the message
	// and display it in the message window.
	let data = JSON.parse(e.data)
	if(data.message.type == "message"){
            getMessageById(data.message.id);
	}
	else{
	    if(data.message.type="status"){
		if(data.message.online){
		    status_button = document.getElementById(`user_${data.message.user_id}`);
		    status_button.innerText = "Online";
		    status_button.classList.remove("btn-danger");
		    status_button.classList.add("btn-success");
		}
		else{
		    status_button = document.getElementById(`user_${data.message.user_id}`);
		    status_button.innerText = "Offline";
		    status_button.classList.remove("btn-success");
		    status_button.classList.add("btn-danger");
		}
	    }
	    
	}
    };
});
