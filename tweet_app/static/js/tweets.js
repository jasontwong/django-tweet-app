// {{{ function csrfSafeMethod(method)
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
// }}}
// {{{ tweeting
( function($){
    'use strict';
    $( function(){
        var form = $( 'form' ),
            buttons = $( 'button', form ),
            message = $( '#message' ),
            rebranded = $( '#rebranded' ),
            tweet = $( '#tweet' ),
            tweet_id = $( '#tweet-id' ),
            text_counter = tweet.next( '.text-counter' ),
            span_num = $( '> span', text_counter ),
            csrftoken = $.cookie( 'csrftoken' ),
            max_chars = 140,
            check_text_limit = function( e ){
                var el = $( this ),
                    text = el.val();
                if ( e.which >= 0x20 )
                {
                    if ( text.length == max_chars )
                    {
                        e.preventDefault();
                    }
                    if ( text.length > max_chars )
                    {
                        text = text.substring( 0, max_chars );
                        el.val( text );
                    }
                }
                span_num.text( text.length );
            };

        tweet
            .each( function(){
                var el = $( this ),
                    text = el.val();
                span_num.text( text.length );
            })
            .on({
                keyup: check_text_limit,
                keypress: check_text_limit,
                change: check_text_limit
            });

        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        buttons
            .on({
                click: function() {
                    var el = $( this );
                    rebranded.hide();
                    buttons.attr( 'disabled', 'disabled' );
                    if ( el.val() === 'publish' ) {
                        $.post( '/tweet_app/ajax/moderate/', { 'id': tweet_id.val(), 'tweet': tweet.val() }, function( data ){
                            var success = false;
                            if ( data.error != null ) {
                                message.text( 'There was an error: ' + data.error );
                                buttons.removeAttr( 'disabled' );
                            } else if ( data.moderate ) {
                                message.text( 'Your tweet was moderated because: ' + data.reasons.join( ', ' ));
                                buttons.removeAttr( 'disabled' );
                            } else {
                                $.post( '/tweet_app/ajax/publish/', { 'id': data.id }, function( publish_data ){
                                    if ( publish_data.success ) {
                                        window.location = publish_data.uri;
                                    } else {
                                        if ( publish_data.error === 'tweet needs to be changed for branding' ) {
                                            message.text( 'Rebrand your tweet please' );
                                            $( '> span', rebranded ).text( publish_data.text );
                                            rebranded.show();
                                        } else {
                                            message.text( 'Unable to publish: ' + publish_data.error );
                                        }
                                        buttons.removeAttr( 'disabled' );
                                    }
                                }, 'json' );
                            }
                        }, 'json' );
                    } else if ( el.val() === 'save' ) {
                        $.post( '/tweet_app/ajax/save/', { 'id': tweet_id.val(), 'tweet': tweet.val() }, function( data ){
                            if ( data.success ) {
                                window.location = data.uri;
                            } else {
                                message.text( 'Unable to save' );
                                buttons.removeAttr( 'disabled' );
                            }
                        }, 'json' );
                    }
                }
            });
        form
            .submit( function(){
                return false;
            });
    });
}( jQuery ));
// }}}
// {{{ listing
( function($){
    'use strict';
    $( function(){
        var csrftoken = $.cookie( 'csrftoken' );
        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        $('.live-retweet')
            .each( function(){
                var el = $( this );
                $.post( '/tweet_app/ajax/get-live-retweets/', { 'id': el.data( 'id' ) }, function( data ){
                    if ( data.success ) {
                        el.text( data.count );
                    }
                }, 'json' );
            });
    });
}( jQuery ));
// }}}
// {{{ shorten url
( function($){
    'use strict';
    $( function(){
        var csrftoken = $.cookie( 'csrftoken' ),
            shorten_div = $( '#url-shorten' ),
            url = $( '> input', shorten_div ),
            control = $( '> a', shorten_div ),
            new_url = $( '> span', shorten_div );
        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        control
            .on({
                click: function(){
                    var el = $( this );
                    $.post( '/tweet_app/ajax/shorten-url/', { 'url': url.val() }, function( data ){
                        if ( data.success ) {
                            console.log( data );
                            new_url.text( data.url );
                        }
                    }, 'json' );
                }
            });
    });
}( jQuery ));
// }}}
