// 'use strict';

// function modalShown(event){
//     let button = event.relatedTarget;
//     let userId = button.dataset.userId;
//     let newUrl = `/users/${userId}/delete`;
//     let form = document.getElementById('deleteModalForm');
//     form.action = newUrl;
// }

// let modal = document.getElementById('deleteModal');
// modal.addEventListener('show.bs.modal', modalShown)
'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('deleteModal');
    modal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const userId = button.dataset.userId;
        const userFio = button.dataset.userFio;

        const form = document.getElementById('deleteModalForm');
        form.action = `/users/${userId}/delete`;

        const userFioSpan = document.getElementById('userFioInModal');
        userFioSpan.textContent = userFio;
    });
});