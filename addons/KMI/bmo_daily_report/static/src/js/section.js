// var target = $('div.o_list_view');
var target = $("div[name='incompatibility_line']");
// console.log('Target : ' + target);
var new_el = "<div class='table-responsive'><table class='o_list_table' style='table-layout: fixed; width: 100%;'><thead><th class='text-center'>Major Breakdown</th><th>Minor Breakdown</th></thead></table></div>"
// var target_step_cip = $("div[name='step_cip_line']").find('.table:first-child');
// console.log('Target : ' + target_step_cip);
// var ell = "<tr><th colspan='2' class='text-center'>Pre Rinse</th><th colspan='2' class='text-center'>Caustic / Lye</th><th colspan='2' class='text-center'>Intermediete rinse</th><th colspan='2' class='text-center'>Acid</th><th colspan='2' class='text-center'>Final Rinse</th><th colspan='3' class='text-center'>Hot Water</th></tr>"
target.prepend(new_el);
// target_step_cip.prepend(ell);