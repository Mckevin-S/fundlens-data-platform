// Filtre instantané du tableau des contrôles (jQuery)
$(function () {
  $("#filter").on("input", function () {
    const term = $(this).val().toLowerCase();
    $("#reports tbody tr").each(function () {
      $(this).toggle($(this).text().toLowerCase().includes(term));
    });
  });
});
