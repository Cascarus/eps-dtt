function getPeriodosVariables() {
    $.ajax({
        url: _URLPERIOD_VARIABLE,
        success: function (e) {
            PERIODOS_VARIABLES = e
        }
    })
}

function getPeriodosSemestre() { 
    $.ajax({ 
        url: _URLPERIOD_SEMESTRE, 
        async: !1, 
        success: function (e) { 
            PERIODOS_SEMESTRE = e
        } 
    }) 
} 

function llenaComboPeriodosVariables(e, f) { 
    if(f){ $("#" + e).empty(); }
    $.each(PERIODOS_VARIABLES, function (o, a) {
        var n = new Option(a.period.name + "-" + a.period_year.yearp, a.period_year.id); 
        $("#" + e).append(n);
    }) 
} 

function llenaComboPeriodosVariablesAjax(e, o) { 
    $("#" + e).empty();
    $.ajax({ 
        url: _URLPERIOD_VARIABLE, 
        async: !0, 
        success: function (a) { 
            PERIODOS_VARIABLES = a;
            $.each(PERIODOS_VARIABLES, function (o, a) { 
                var n = new Option(a.period.name + "-" + a.period_year.yearp, a.period_year.id); 
                $("#" + e).append(n) 
            })
            if(o){ $("#" + e).val(o) }
        }
    }) 
} 
        
function llenaComboPeriodosSemestres(e, f) {
    if(f){ $("#" + e).empty(); }
    $.each(PERIODOS_SEMESTRE, function (o, a) { 
        var n = new Option(a.period.name + "-" + a.period_year.yearp, a.period_year.id); 
        $("#" + e).append(n) 
    }) 
} 
    
function llenaComboPeriodosSemestresAjax(e, o) { 
    $("#" + e).empty();
    $.ajax({ 
        url: _URLPERIOD_SEMESTRE, 
        async: true, 
        success: function (a) {
            PERIODOS_SEMESTRE = a;
            $.each(PERIODOS_SEMESTRE, function (o, a) { 
                var n = new Option(a.period.name + "-" + a.period_year.yearp, a.period_year.id);
                $("#" + e).append(n) 
            })
            if(o) { $("#" + e).val(o) }
        } 
    }) 
} 
                
function exportTableToExcel(e) { 
    var o = document.querySelector("#" + e); 
    TableToExcel.convert(o) 
} 

function refreshData() { 
    $.ajax({ 
        type: "POST", 
        url: _URLNOTIFICATION_NUMBER, 
        data: userName, 
        success: function (e) { 
            $(".dttInbox").html("Bandeja de Entrada <span class='badge badge-danger'>" + e + "</span>") 
        } 
    }) 
} 

$("#sidenavToggler").click(function (e) { 
    e.preventDefault();
    $("body").toggleClass("sidenav-toggled"); 
    $(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
    $(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show") 
});

$("#chkTipoCurso").change(function () { 
    $(this).prop("checked") ? llenaComboPeriodosSemestres("period") : llenaComboPeriodosVariables("period") 
}); 

if ("None" == periodo) { 
    $("#chkTipoCurso").attr("checked");
    setTimeout(function () { 
        llenaComboPeriodosSemestres("period", true);
        $("#period").val(periodo); 
    }, 1000)
} else { 
    if("None" == tipo_periodo) { 
        $("#chkTipoCurso").removeAttr("checked");
        setTimeout(function () { 
            llenaComboPeriodosVariables("period"); 
            $("#period").val(periodo) 
        }, 1000)
    } else {
        $("#chkTipoCurso").attr("checked");
        setTimeout(function () { 
            llenaComboPeriodosSemestres("period");
            $("#period").val(periodo) 
        }, 1000)
    }
} 
 
window.onload = function () { 
    setTimeout(function () { 
        if ($(".w2p_flash").is(":visible")) { 
            setTimeout(function () { 
                $(".w2p_flash").hide() 
            }, 1000)
        }
    }, 5000)
};