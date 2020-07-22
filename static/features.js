/*
    FEATURES - Diogo Venâncio & André Gonçalves
*/

/* PROJECTS */
function loadProjects() {
    console.log('loading projects');

    var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/");
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            showProjects(JSON.parse(this.responseText));
        }
    }
    req.send();
}

function createProject() {
    console.log('creating project');

    var req = new XMLHttpRequest();
    req.open("POST", "/api/projects/");
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 201) {
            loadProjects();
        }
    }

    let projectTitle = $('.input--project-name').val();
    $('.input--project-name').val("");
    let params = JSON.stringify({
        title: projectTitle,
		description: "description"
    });

    req.send(params);
}

function deleteProject(e) {
    if (!confirm("Are you sure you want to delete this project?")) {
        return;
    }

    let projectId = getProjectIdFromElement($(e.target));

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/";
    req.open("DELETE", uri);
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status === 200) {
                loadProjects();
            } else if (this.status === 403) {
                alert("You don't have permission to do that!");
            }
        }
    }
    req.send();
}

/* TASKS */
function loadTasks(projectId) {
    let destination = $('#project-' + projectId + " .project-tasks");

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/tasks/";
    req.open("GET", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            showTasks(destination, JSON.parse(this.responseText));
        }
    }
    req.send();
}

function addTask(task) {
    let projectId = getProjectIdFromElement($(task));
    if (!$(task).hasClass('project-task')) {
        task = $(task).parent();
    }
    let taskName = $(task).find('input').val();
    if (taskName == "") {
        return;
    }
    $(task).find('input').val("");

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/tasks/";
    req.open("POST", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 201) {
            loadTasks(projectId);
        }
    }

    let projectTitle = $('.input--project-name').val();
    let params = JSON.stringify({
        project_id: projectId,
        description: taskName
    });

    req.send(params);
}

function deleteTask(e) {
    let projectId = getProjectIdFromElement($(e.target));
    let taskId = getTaskIdFromElement($(e.target));

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/tasks/" + taskId + "/";
    req.open("DELETE", uri);
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            loadTasks(projectId);
        }
    }
    req.send();
}


function toggleTaskState(e) {
    $(e.target).closest('.project-task').toggleClass('completed');
    updateTask($(e.target));
}

function updateTask(task) {
    let projectId = getProjectIdFromElement($(task));
    let taskId = getTaskIdFromElement($(task));

    if (!$(task).hasClass('project-task')) {
        task = $(task).parent();
    }

    let taskText = $(task).find("input").val();
    console.log($(task));
    let completed = $(task).hasClass('completed');
    let order = $(task).index();


    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/tasks/" + taskId + "/";
    req.open("PUT", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 201) {
            loadTasks(projectId);
        }
    }

    let projectTitle = $('.input--project-name').val();
    let params = JSON.stringify({
        project_order: order,
        description: taskText,
        status: +completed
    });
    console.log(params);

    req.send(params);
}

/* COLLABORATORS */
function loadCollaborators(projectId) {
    let destination = $('#project-' + projectId + " .project-collaborators");

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/collaborators/";
    req.open("GET", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            showCollaborators(destination, JSON.parse(this.responseText));
        }
    }
    req.send();
}

function addCollaborator(e) {
    let projectId = getProjectIdFromElement($(e.target));

    let collaborator = prompt("Username of collaborator:");
    if (collaborator == "") {
        return;
    }

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/collaborators/";
    req.open("POST", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status === 201) {
                loadCollaborators(projectId);
            } else if (this.status === 404) {
                alert("Collaborator not found!");
            }

        }
    }

    let projectTitle = $('.input--project-name').val();
    let params = JSON.stringify({
        username: collaborator
    });
    req.send(params);
}

function removeCollaborator(e) {
    let projectId = getProjectIdFromElement($(e.target));
    let collaboratorId = getCollaboratorIdFromElement($(e.target));

    let result = confirm("Are you sure you want to remove this collaborator?");
    if (!result) {
        return;
    }

    var req = new XMLHttpRequest();
    let uri = "/api/projects/" + projectId + "/collaborators/" + collaboratorId + "/";
    req.open("DELETE", uri);
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status === 200) {
                loadCollaborators(projectId);
            } else if (this.status === 403) {
                alert("You don't have permission to do that!");
            }
        }
    }

    let projectTitle = $('.input--project-name').val();
    let params = JSON.stringify({
        collaborator: collaboratorId
    });
    req.send(params);
}

/* FUNCTIONS */
function applySortable() {
    $(".sortable").sortable({
        axis: 'y',
        containment: "parent",
        update: function (event, ui) {
            updateTasksOrder(ui.item);
        }
    });
}


function showProjects(projects) {
    console.log(projects);
    $('.project-viewer').empty();

    $.each(projects, function (i, project) {
        let date = project.last_update.slice(0, -7);
        $('.project-viewer').append(
            `
            <div id="project-${project.id}" class="project-card">
            <div class="project-card-header">
                <div class="project-name">${project.title}</div>
                <div class="project-edited">${date}</div>
            </div>
            <ul class="sortable project-tasks">
            </ul>
            <div class="project-task add-task">
                <i class="material-icons ">add</i>
                <input type="text">
            </div>
            <div class="project-actions">
                <i class="material-icons project-add-person">person_add</i>
                <i class="material-icons project-delete">delete</i>
                <i class="material-icons project-chat">chat</i>
                <div class="project-collaborators"></div>
            </div>

        </div>`
        );
        loadTasks(project.id);
        loadCollaborators(project.id);
    });
}


function showTasks(destination, tasks) {
    $(destination).empty();
    console.log(tasks);
    $.each(tasks, function (i, task) {
        let status = "";
        if (task.status == 1) status = "completed";
        $(destination).append(
            `
                <li id="task-${task.id}" class="project-task ${status}">
                    <i class="material-icons drag">drag_indicator</i>
                    <i class="material-icons checkbox">check_box_outline_blank</i>
                    <i class="material-icons checkbox">check_box</i>
                    <input type="text" value="${task.description}">
                    <i class="material-icons delete-task">close</i>

                </li>`
        );
    });
    applySortable();
}

function showCollaborators(destination, collaborators) {
    console.log(collaborators);
    $(destination).empty();

    $.each(collaborators, function (i, collab) {
        let initial = collab.username.charAt(0).toUpperCase();
        $(destination).append(`
        <div id="collaborator-${collab.id}" title="${collab.username}" class="collaborator">${initial}
            <i class="material-icons remove-collaborator">close</i>
        </div>
    `)
    })
}


function updateTasksOrder(item) {
    let projectId = getProjectIdFromElement(item);
    let children = $('#project-' + projectId + ' ul').children();
    $.each(children, function (i, task) {
        updateTask(task);
    });
}

function getProjectIdFromElement(elem) {
    let parent = elem.closest('.project-card');
    return $(parent).attr('id').split('-')[1];
}

function getTaskIdFromElement(elem) {
    let parent = elem.closest('.project-task');
    return $(parent).attr('id').split('-')[1];
}

function getCollaboratorIdFromElement(elem) {
    let parent = elem.closest('.collaborator');
    return $(parent).attr('id').split('-')[1];
}