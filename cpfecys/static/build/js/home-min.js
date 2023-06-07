function getPeriodosVariables(){
    $.ajax({
        url:_URLPERIOD_VARIABLE,
        success:function(e){
            var o = e;
            o && (PERIODOS_VARIABLES = o)
        }
    })
}

function getPeriodosSemestre(){
    $.ajax({
        url: _URLPERIOD_SEMESTRE,
        async: !1,
        success: function(e){
            var o = e;
            o && (PERIODOS_SEMESTRE = o)
        }
    })
}

function llenaComboPeriodosVariables(e){
    $("#" + e).empty(), $.each(PERIODOS_VARIABLES, function(o,r) {
        var a = new Option(r.period.name + "-" + r.period_year.yearp, r.period_year.id);
        $("#" + e).append(a)
    })
}

function llenaComboPeriodosVariablesAjax(e, o){
    $("#" + e).empty(), $.ajax({
        url: _URLPERIOD_VARIABLE,
        async: !0,
        success: function(r){
            var a = r;
            a && (PERIODOS_VARIABLES = a, $.each(PERIODOS_VARIABLES,function(o,r) {
                    var a = new Option(r.period.name + "-" + r.period_year.yearp, r.period_year.id);
                    $("#" + e).append(a)
                }), o && $("#"+e).val(o)
            )
        }
    })
}

function llenaComboPeriodosSemestres(e) {
    $("#" + e).empty(), $.each(PERIODOS_SEMESTRE, function(o, r){
        var a = new Option(r.period.name + "-" + r.period_year.yearp, r.period_year.id);
        $("#" + e).append(a)
    })
}

function llenaComboPeriodosSemestresAjax(e, o){
    $("#" + e).empty(), $.ajax({
        url:_URLPERIOD_SEMESTRE,
        async:!0,
        success:function(r){
            var a = r;
            a && (PERIODOS_SEMESTRE = a, $.each(PERIODOS_SEMESTRE, function(o, r){
                var a = new Option(r.period.name + "-" + r.period_year.yearp, r.period_year.id);
                $("#" + e).append(a)
            }), o && $("#"+e).val(o)
            )
        }
    })
}

$.ajax({
    url:_URLPERIOD_SEMESTRE,
    async:!1,
    success:function(e){
        if(e){
            var o = e;
            PERIODOS_SEMESTRE=o
        }
        $.ajax({
            url:_URLPERIOD_VARIABLE,
            success:function(e){
                var o = e;
                o && (PERIODOS_VARIABLES=o)
            }
        })
    }
}), $("#chkTipoCurso").change(function(){
    $(this).prop("checked") ? llenaComboPeriodosSemestres("period"): llenaComboPeriodosVariables("period")}),"None" == periodo ? ($("#chkTipoCurso").attr("checked"),setTimeout(function(){
        llenaComboPeriodosSemestres("period"), $("#period").val(periodo)
    },1e3)): "None" == tipo_periodo ? ($("#chkTipoCurso").removeAttr("checked"),setTimeout(function(){
        llenaComboPeriodosVariables("period"), $("#period").val(periodo)},1e3)) : ($("#chkTipoCurso").attr("checked"),setTimeout(function(){
            llenaComboPeriodosSemestres("period"),$("#period").val(periodo)},1e3));
            for(var youtube=document.querySelectorAll(".youtube"),i=0;i<youtube.length;i++){
                var source="https://img.youtube.com/vi/"+youtube[i].dataset.embed+"/sddefault.jpg",image=new Image;
                image.src=source,image.addEventListener("load",void youtube[i].appendChild(image)),youtube[i].addEventListener("click",function(){
                    var e=document.createElement("iframe");
                    e.setAttribute("frameborder","0"),e.setAttribute("allowfullscreen",""),e.setAttribute("src","https://www.youtube.com/embed/"+this.dataset.embed+"?rel=0&showinfo=0&autoplay=1"),this.innerHTML="",this.appendChild(e)})
                }