document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formSigno');
    const inputData = document.getElementById('data_nascimento');

    // Define a data máxima como o dia de hoje
    const hoje = new Date().toISOString().split('T')[0];
    inputData.setAttribute('max', hoje);

    form.addEventListener('submit', function (event) {
        if (!inputData.value) {
            event.preventDefault();
            alert('Por favor, selecione uma data de nascimento válida!');
        }
    });
});