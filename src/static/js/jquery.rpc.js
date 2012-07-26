/* jQuery.Rpc */
/* Examples and some documetation here: https://github.com/Alerion/jQuery-Utils */
(function($){
 
    $.Rpc = $.inherit(jQuery.util.Observable, {
        exceptions: {
            TRANSPORT: 'xhr',
            PARSE: 'parse',
            LOGIN: 'login',
            SERVER: 'exception'
        },
      
        constructor: function(){
            this.addEvents(
                'event',
                'exception'
            );
            this.transactions = {};
            this.providers = {};
        },
        
        addProvider : function(provider){
            var a = arguments;
            if(a.length > 1){
                for(var i = 0, len = a.length; i < len; i++){
                    this.addProvider(a[i]);
                }
                return;
            }
              
            if(!provider.events){
                provider = new $.Rpc.RemotingProvider(provider);
            }
            provider.id = provider.id || $.guid++;
            this.providers[provider.id] = provider;
    
            provider.on('data', this.onProviderData, this);
            provider.on('exception', this.onProviderException, this);
    
            if(!provider.isConnected()){
                provider.connect();
            }
    
            return provider;
        },
    
        
        getProvider : function(id){
            return this.providers[id];
        },
    
        removeProvider : function(id){
            var provider = id.id ? id : this.providers[id];
            provider.un('data', this.onProviderData, this);
            provider.un('exception', this.onProviderException, this);
            delete this.providers[provider.id];
            return provider;
        },
    
        addTransaction: function(t){
            this.transactions[t.tid] = t;
            return t;
        },
    
        removeTransaction: function(t){
            delete this.transactions[t.tid || t];
            return t;
        },
    
        getTransaction: function(tid){
            return this.transactions[tid.tid || tid];
        },
    
        onProviderData : function(provider, e){
            if($.isArray(e)){
                for(var i = 0, len = e.length; i < len; i++){
                    this.onProviderData(provider, e[i]);
                }
                return;
            }
            if(e.name && e.name != 'event' && e.name != 'exception'){
                this.fireEvent(e.name, e);
            }else if(e.type == 'exception'){
                this.fireEvent('exception', e);
            }
            this.fireEvent('event', e, provider);
        },
    
        createEvent : function(response, extraProps){
            return new $.Rpc.eventTypes[response.type]($.extend(response, extraProps));
        }
    });

    $.Rpc = new $.Rpc();

    $.Rpc.TID = 1;
    
    //Transaction
    $.Rpc.Transaction = function(config){
        $.extend(this, config);
        this.tid = ++$.Rpc.TID;
        this.retryCount = 0;
    };

    $.Rpc.Transaction.prototype = {
        send: function(){
            this.provider.queueTransaction(this);
        },
    
        retry: function(){
            this.retryCount++;
            this.send();
        },
    
        getProvider: function(){
            return this.provider;
        }
    };
    
    //Event
    $.Rpc.Event = function(config){
        $.extend(this, config);
    };

    $.Rpc.Event.prototype = {
        status: true,
        getData: function(){
            return this.data;
        }
    };
    
    $.Rpc.RemotingEvent = $.inherit($.Rpc.Event, {
        type: 'rpc',
        getTransaction: function(){
            return this.transaction || $.Rpc.getTransaction(this.tid);
        }
    });
    
    $.Rpc.ExceptionEvent = $.inherit($.Rpc.RemotingEvent, {
        status: false,
        type: 'exception'
    });

    $.Rpc.eventTypes = {
        'rpc':  $.Rpc.RemotingEvent,
        'event':  $.Rpc.Event,
        'exception':  $.Rpc.ExceptionEvent
    };
    
    //Provider
    $.Rpc.Provider = $.inherit($.util.Observable, {
        
        priority: 1,
        
        constructor : function(config){
            $.extend(this, config);
            this.addEvents(
                'connect',
                'disconnect',
                'data',
                'exception'
            );
            $.Rpc.Provider.superclass.constructor.call(this, config);
        },
        
        isConnected: function(){
            return false;
        },
        
        connect: $.noop,
        
        disconnect: $.noop
    });
    
    $.Rpc.JsonProvider = $.inherit($.Rpc.Provider, {
        parseResponse: function(xhr){
            if(!$.isEmpty(xhr.responseText)){
                if(typeof xhr.responseText == 'object'){
                    return xhr.responseText;
                }
                return $.parseJSON(xhr.responseText);
            }
            return null;
        },
    
        getEvents: function(xhr){
            var data = null;
            try{
                data = this.parseResponse(xhr);
            }catch(e){
                var event = new $.Rpc.ExceptionEvent({
                    data: e,
                    xhr: xhr,
                    code: $.Rpc.exceptions.PARSE,
                    message: 'Error parsing json response: \n\n ' + data
                });
                return [event];
            }
            var events = [];
            if($.isArray(data)){
                for(var i = 0, len = data.length; i < len; i++){
                    events.push($.Rpc.createEvent(data[i]));
                }
            }else{
                events.push($.Rpc.createEvent(data));
            }
            return events;
        }
    });
    
    $.Rpc.RemotingProvider = $.inherit($.Rpc.JsonProvider, {
        enableBuffer: 10,
        
        maxRetries: 1,
        
        timeout: undefined,
    
        constructor : function(config){
            $.Rpc.RemotingProvider.superclass.constructor.call(this, config);
            this.addEvents(
                'beforecall',
                'call'
            );
            this.namespace = (typeof this.namespace == 'string') ? $.ns(this.namespace) : this.namespace || window;
            this.transactions = {};
            this.callBuffer = [];
        },
        
        initAPI : function(){
            var o = this.actions;
            for(var c in o){
                var cls = this.namespace[c] || (this.namespace[c] = {}),
                    ms = o[c];
                for(var i = 0, len = ms.length; i < len; i++){
                    var m = ms[i];
                    cls[m.name] = this.createMethod(c, m);
                }
            }
        },
        
        isConnected: function(){
            return !!this.connected;
        },
    
        connect: function(){
            if(this.url){
                this.initAPI();
                this.connected = true;
                this.fireEvent('connect', this);
            }else if(!this.url){
                throw 'Error initializing RemotingProvider, no url configured.';
            }
        },
    
        disconnect: function(){
            if(this.connected){
                this.connected = false;
                this.fireEvent('disconnect', this);
            }
        },
    
        onData: function(xhr, status, transactions){
            var i, len, e, t;
            if(status === 'success'){
                var events = this.getEvents(xhr);
                for(i = 0, len = events.length; i < len; i++){
                    e = events[i];
                    t = this.getTransaction(e);
                    this.fireEvent('data', this, e);
                    if(t){
                        this.doCallback(t, e, true);
                        $.Rpc.removeTransaction(t);
                    }
                }
            }else{
                var ts = [].concat(transactions);

                for(i = 0, len = ts.length; i < len; i++){
                    t = this.getTransaction(ts[i]);

                    if(t && t.retryCount < this.maxRetries){
                        t.retry();
                    }else{
                        e = new $.Rpc.ExceptionEvent({
                            data: ts[i].data,
                            transaction: t,
                            code: $.Rpc.exceptions.TRANSPORT,
                            message: 'Unable to connect to the server.',
                            xhr: xhr
                        });
                        this.fireEvent('data', this, e);
                        if(t){
                            this.doCallback(t, e, false);
                            $.Rpc.removeTransaction(t);
                        }
                    }
                }
            }
        },
    
        getCallData: function(t){
            if (t.form){
                return {
                    rpcAction: t.action,
                    rpcMethod: t.method,
                    rpcTID: t.tid,
                    rpcUpload: $('input:file:enabled[value]', t.form).length > 0
                };
            } else {
                return {
                    action: t.action,
                    method: t.method,
                    data: t.data,
                    tid: t.tid
                };
            }
        },
    
        doSend : function(t){
            var o = {
                url: this.url,
                ts: t,
                type: 'POST',
                timeout: this.timeout,
                dataType: 'json'
            }, callData;
    
            if($.isArray(t)){
                callData = [];
                for(var i = 0, len = t.length; i < len; i++){
                    callData.push(this.getCallData(t[i]));
                }
            }else{
                callData = this.getCallData(t);
            }

            if(this.enableUrlEncode){
                var params = {};
                params[(typeof this.enableUrlEncode == 'string') ? this.enableUrlEncode : 'data'] = $.JSON.encode(callData);
                o.data = $.param(params);
            }else{
                o.data = encodeURIComponent($.JSON.encode(callData));
                o.processData = false;
            }
            
            o.complete = this.onData.createDelegate(this, t, true);
            $.ajax(o);
        },
    
        combineAndSend : function(){
            var len = this.callBuffer.length;
            if(len > 0){
                this.doSend(len == 1 ? this.callBuffer[0] : this.callBuffer);
                this.callBuffer = [];
            }
        },

        processForm: function(t){
            // TODO: allow jquery.form use proper way to send form, not just iframe
            // now problem is in response, RPC backend send data in <textarea> when
            // fileUploadXhr tries parse json
            t.form.ajaxSubmit({
                iframe: true,
                data: $.extend({}, this.getCallData(t), t.data),
                dataType: 'json',
                complete: this.onData.createDelegate(this, t, true),
                type: 'POST',
                timeout: this.timeout,
                url: this.url
            });
        },

        queueTransaction: function(t){
            if(t.form){
                // TODO: form is processed not in butch
                this.processForm(t);
                return;
            }
            this.callBuffer.push(t);
            if(this.enableBuffer){
                if(!this.callTask){
                    this.callTask = new $.util.DelayedTask(this.combineAndSend, this);
                }
                this.callTask.delay($.isNumber(this.enableBuffer) ? this.enableBuffer : 10);
            }else{
                this.combineAndSend();
            }
        },

        doCall : function(c, m, args){
            var data = null, form = null, cb, scope, len = 0;

            if (m.formHandler){
                form = args[0];
                len = 1;

                // extra data
                if ($.isObject(args[1])){
                    data = args[1];
                    len = 2;
                }
            }else{
                // Find out arguments number and get them
                $.each(args, function(i, val){
                    if ($.isFunction(val)){
                        return false;
                    }
                    len = i+1;
                });

                if(len !== 0){
                    data = args.slice(0, len);
                }
            }
            
            // Get callbacks
            if (args[len+1] && $.isFunction(args[len+1])){
                //we have failure callback after success one
                scope = args[len+2];
                cb = {
                    success: scope && $.isFunction(args[len]) ? args[len].createDelegate(scope) : args[len],
                    failure: scope ? args[len+1].createDelegate(scope) : args[len+1]
                };
                scope = args[len+2];
            }else{
                // no failure callback after success one
                scope = args[len+1];
                cb = args[len] || $.noop;
                cb = scope && $.isFunction(cb) ? cb.createDelegate(scope) : cb;
            }

            var t = new $.Rpc.Transaction({
                provider: this,
                args: args,
                action: c,
                method: m.name,
                data: data,
                form: form,
                cb: cb
            });
    
            if(this.fireEvent('beforecall', this, t) !== false){
                $.Rpc.addTransaction(t);
                this.queueTransaction(t);
                this.fireEvent('call', this, t);
            }
        },
        createMethod : function(c, m){
            var f = function(){
                this.doCall(c, m, Array.prototype.slice.call(arguments, 0));
            }.createDelegate(this);
            f.directCfg = {
                action: c,
                method: m
            };
            return f;
        },
    
        getTransaction: function(opt){
            return opt && opt.tid ? $.Rpc.getTransaction(opt.tid) : null;
        },
    
        doCallback: function(t, e){
            var fn = e.status ? 'success' : 'failure';
            if(t && t.cb){
                var hs = t.cb,
                    result = $.isDefined(e.result) ? e.result : e.data;
                if($.isFunction(hs)){
                    hs(result, e);
                } else{
                    hs[fn].apply(hs.scope, [result, e]);
                }
            }
        }
    });
     
})(jQuery);


