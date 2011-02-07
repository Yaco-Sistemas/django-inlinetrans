(function ($) {
    String.format = String.format || function(format){
        var args = Array.prototype.slice.call(arguments, 1);
        return format.replace(/\{(\d+)\}/g, function(m, i){
            return args[i];
        });
    };

    $.fn.inlinetranstoolbar = function(toolbar_tpl, new_translation_url, restart_url, messages_dict) {
        return this.each(function() {
            $(this).html(toolbar_tpl);
            var some_changes = false;
            var send_translation = function () {
                var msgid = $(this).attr('rel');
                var untranslated = false;
                var old_msgstr = $(this).html() ;
                var msgstr = prompt(String.format(messages_dict.givetranslationfor, msgid), old_msgstr);
                if (msgstr == null){
                    return false;
                }
                if (msgstr == ""){
                    answer = confirm(messages_dict.emptytranslation);
                    var msgstr = "";
                }
                else {
                    answer = true;
                }
                if(answer){
                    var item = $(this);
                    active_loading();
                    jsondata = $.param({msgid:msgid, msgstr:msgstr});
                    $.ajax({
                        data: jsondata,
                        url: new_translation_url,
                        type: "POST",
                        async: true,
                        success: function(response){
                            item.html(msgstr || msgid);
                            some_changes = true;
                            disable_loading();
                            active_restart();
                        },
                        error: function(response){
                            alert(messages_dict.error_cant_send);
                            disable_loading();
                        }
                    });
                }
                return false;
            }
            var active_translation = false;

            var active_translations = function () {
                if ($("span.inlinetransActions span.active").length && !active_translation) {
                    active_translation = true;
                    $("a > span.translatable").each(function(){
                        $(this).parent().click(function () {
                            return false;
                        });
                    });
                    $("span.translatable").click(send_translation);
                }
            }

            var active_loading = function() {
                $("img#changes-loading").show();
            }

            var disable_loading = function() {
                $("img#changes-loading").hide();
            }

            var disable_translations = function () {
                if ($("span.inlinetransActions span.active").length == 0 && active_translation) {
                    active_translation = false;
                    $("span.translatable").unbind("click", send_translation);
                    $("a > span.translatable").each(function(){
                        $(this).parent().unbind('click');
                    });
                }
            }

            $("span.hightlightTrans").click(function () {
                $("span.translatable").toggleClass("inlinetransHighlight");
                $(this).toggleClass("active");
                if ($(this).hasClass("active")) {
                    active_translations();
                }
                else {
                    disable_translations();
                }
            });

            $("span.hightlightNotrans").click(function(){
                $(this).toggleClass("active");
                if ($(this).hasClass("active")) {
                    active_translations();
                }
                else {
                    disable_translations();
                }
                $("span.untranslated").toggleClass("inlinetransUntranslated");
            });

            active_restart = function () {
                $("span.restartServer").css({display: 'inline'});
                $("span.restartServer").click(function(){
                    if (some_changes){
                        $("span.restartServer").html(messages_dict.applying_changes);
                        $(this).toggleClass("active");
                        active_loading();
                        $.ajax({
                                data: "",
                                url: restart_url,
                                type: "POST",
                                async: true,
                                success: function(response){
                                    some_changes = false;
                                    $("span.restartServer").html(messages_dict.reloading);
                                    setTimeout(function(){
                                    document.location = document.location;
                                    $("span.restartServer").html(messages_dict.apply_changes);
                                    $("span.restartServer").toggleClass("active");
                                    disable_loading();
                                    }, parseInt(response) * 1000);
                                },
                                error: function(response){
                                    alert(messages_dict.error_cant_restart);
                                    disable_loading();
                                }
                        });
                    }
                });
            }
        });
    };
})(jQuery);
