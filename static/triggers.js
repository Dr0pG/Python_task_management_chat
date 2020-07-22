/*
    TRIGGERS - Diogo Venâncio & André Gonçalves
*/

//$('#newProject').on('click', createProject);
$(document).on('click', '#newProject', createProject);

$(document).on('keyup', '.project-creator input', function (e) {
    if (e.keyCode != 13) {
        return;
    }

    createProject(e);
})


$(document).on('click', '.project-delete', deleteProject);

$(document).on('click', '.add-task i', function(e){
    addTask(e.target);
});

$(document).on('keyup', '.add-task input', function (e) {
    if (e.keyCode != 13) {
        return;
    }

    addTask(e.target);
});

$(document).on('keyup', '.project-task:not(".add-task") input', function (e) {
    if (e.keyCode != 13) {
        return;
    }

    updateTask(e.target);
});

$(document).on('click', 'i.delete-task', deleteTask);
$(document).on('click', 'i.checkbox', toggleTaskState);
$(document).on('click', '.project-add-person', addCollaborator);
$(document).on('click', 'i.remove-collaborator', removeCollaborator);
$(document).on('click', '.menu .logout', logout);
$(document).on('click', '.menu .account', openAccount);
$(document).on('click', '.menu .projects', openProjects);
