// Refrescar div automaticamente sin recargar la pagina

setInterval(
    function() {
        $("#reload").load(location.href+" #reload>*","");
    }, 
3000);
