
/**
 * @see https://github.com/Alerion/Django-RPC/
 */
djangoRPC.RPC = (function($, utils){

    var RPC = {
        TID: 1,
        guid: 0,

        observer: new utils.Observer(),
        transactions: {},
        providers: {},

        transport: null,

        exceptions: {
            TRANSPORT: 'xhr',
            PARSE: 'parse',
            LOGIN: 'login',
            SERVER: 'exception'
        },

        addProvider: function(provider){
            var a = arguments;
            if(a.length > 1){
                for(var i = 0, len = a.length; i < len; i++){
                    this.addProvider(a[i]);
                }
                return;
            }

            if(!provider.events){
                provider = new RPC.RemotingProvider(provider);
            }
            provider.id = provider.id || RPC.guid++;
            this.providers[provider.id] = provider;

            provider.observer.addListener('data', this.onProviderData, this);
            provider.observer.addListener('exception', this.onProviderException, this);

            if(!provider.isConnected()){
                provider.connect();
            }

            return provider;
        },


        getProvider: function(id){
            return this.providers[id];
        },

        removeProvider : function(id){
            var provider = id.id ? id : this.providers[id];
            provider.observer.removeListener('data', this.onProviderData, this);
            provider.observer.removeListener('exception', this.onProviderException, this);
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

        onProviderData: function(provider, e){
            if(e instanceof Array){
                for(var i = 0, len = e.length; i < len; i++){
                    this.onProviderData(provider, e[i]);
                }
                return;
            }
            if(e.name && e.name != 'event' && e.name != 'exception'){
                this.observer.fireEvent(e.name, e);
            }else if(e.type == 'exception'){
                this.observer.fireEvent('exception', e);
            }
            this.observer.fireEvent('event', e, provider);
        },

        createEvent: function(response, extraProps){
            return new RPC.eventTypes[response.type](utils.merge(response, extraProps));
        }
    };

    RPC.observer.addEvents(
        'event',
        'exception'
    );


    //Transaction
    RPC.Transaction = utils.define({
        __init__: function(config){
            utils.merge(this, config);
            this.tid = ++RPC.TID;
            this.retryCount = 0;
        },
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
    });


    //Event
    RPC.Event = utils.define({
        status: true,
        __init__: function(config){
            utils.merge(this, config);
        },
        getData: function(){
            return this.data;
        }
    });


    RPC.RemotingEvent = utils.define({
        __super__: RPC.Event,
        type: 'rpc',
        getTransaction: function(){
            return this.transaction || RPC.getTransaction(this.tid);
        }
    });


    RPC.ExceptionEvent = utils.define({
        __super__: RPC.RemotingEvent,
        status: false,
        type: 'exception'
    });


    RPC.eventTypes = {
        'rpc':  RPC.RemotingEvent,
        'event':  RPC.Event,
        'exception':  RPC.ExceptionEvent
    };


    //Provider
    RPC.Provider = utils.define({

        priority: 1,
        observer: new utils.Observer(),

        __init__ : function(config){
            utils.merge(this, config);

            this.observer.addEvents(
                'connect',
                'disconnect',
                'data',
                'exception'
            );
            // RPC.Provider.__super__.call(this, config);
        },

        isConnected: function(){
            return false;
        },

        connect: utils.noop,
        disconnect: utils.noop
    });


    RPC.JsonProvider = utils.define({
        __super__: RPC.Provider,

        parseResponse: function(xhr){
            if(typeof(xhr.responseText) === 'string'){
                return JSON.parse(xhr.responseText);
            }
            if(typeof xhr.responseText === 'object'){
                return xhr.responseText;
            }
            return null;
        },

        getEvents: function(xhr){
            var data = null;
            try{
                data = this.parseResponse(xhr);
            }catch(e){
                var event = new RPC.ExceptionEvent({
                    data: e,
                    xhr: xhr,
                    code: RPC.exceptions.PARSE,
                    message: 'Error parsing json response: \n\n ' + data
                });
                return [event];
            }
            var events = [];
            if(data instanceof Array){
                for(var i = 0, len = data.length; i < len; i++){
                    events.push(RPC.createEvent(data[i]));
                }
            }else{
                events.push(RPC.createEvent(data));
            }
            return events;
        }
    });


    RPC.RemotingProvider = utils.define({
        __super__: RPC.JsonProvider,

        enableBuffer: 10,
        maxRetries: 1,
        timeout: undefined,

        __init__ : function(config){
            RPC.RemotingProvider.__super__.call(this, config);
            this.observer.addEvents(
                'beforecall',
                'call'
            );
            this.namespace = (typeof this.namespace == 'string') ? utils.namespace(this.namespace) : this.namespace || window;
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
                this.observer.fireEvent('connect', this);
            }else if(!this.url){
                throw 'Error initializing RemotingProvider, no url configured.';
            }
        },

        disconnect: function(){
            if(this.connected){
                this.connected = false;
                this.observer.fireEvent('disconnect', this);
            }
        },

        onData: function(transactions, xhr, status){
            var i, len, e, t;

            if(status === 'success'){
                var events = this.getEvents(xhr);
                for(i = 0, len = events.length; i < len; i++){
                    e = events[i];
                    t = this.getTransaction(e);

                    this.observer.fireEvent('data', this, e);
                    if(t){
                        this.doCallback(t, e);
                        RPC.removeTransaction(t);
                    }
                }
            }else{
                var ts = [].concat(transactions);

                for(i = 0, len = ts.length; i < len; i++){
                    t = this.getTransaction(ts[i]);

                    if(t && t.retryCount < this.maxRetries){
                        t.retry();
                    }else{
                        e = new RPC.ExceptionEvent({
                            data: ts[i].data,
                            transaction: t,
                            code: RPC.exceptions.TRANSPORT,
                            message: 'Unable to connect to the server.',
                            xhr: xhr
                        });
                        this.observer.fireEvent('data', this, e);
                        if(t){
                            this.doCallback(t, e);
                            RPC.removeTransaction(t);
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
                    rpcUpload: $('input:file:enabled', t.form).length > 0
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
            if(t instanceof Array){
                var callData = [];
                for(var i = 0, len = t.length; i < len; i++){
                    callData.push(this.getCallData(t[i]));
                }
            }else{
                var callData = this.getCallData(t);
            }
            
            var encodedData = utils.JSON.encode(callData);
            var completeCallback = this.onData.bind(this, t);
            
            djangoRPC.RPC.transport(this, t, encodedData, completeCallback);
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
                data: utils.merge({}, this.getCallData(t), t.data),
                dataType: 'json',
                complete: this.onData.bind(this, t),
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
                    this.callTask = new utils.DelayedTask(this.combineAndSend, this);
                }
                this.callTask.delay(
                    typeof(this.enableBuffer) === 'number' && isFinite(this.enableBuffer)
                        ? this.enableBuffer
                        : 10
                );
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
                if (utils.isObject(args[1])){
                    data = args[1];
                    len = 2;
                }
            }else{
                // TODO: figure out how does it work and write simpler
                // Find out arguments number and get them
                for (var argIndex = 0, argsLength = args.length; argIndex < argsLength; argIndex += 1)
                {
                    if (typeof(args[argIndex]) === 'function')
                    {
                        break;
                    }

                    len = argIndex + 1;
                }

                if(len !== 0){
                    data = args.slice(0, len);
                }
            }

            // Get callbacks
            if (args[len+1] && typeof(args[len+1]) === 'function'){
                //we have failure callback after success one
                scope = args[len+2];
                cb = {
                    success: scope && typeof(args[len]) === 'function' ? args[len].bind(scope) : args[len],
                    failure: scope ? args[len+1].bind(scope) : args[len+1]
                };
                scope = args[len+2];
            }else{
                // no failure callback after success one
                scope = args[len+1];
                cb = args[len] || utils.noop;
                cb = scope && typeof(cb) === 'function' ? cb.bind(scope) : cb;
            }

            var t = new RPC.Transaction({
                provider: this,
                args: args,
                action: c,
                method: m.name,
                data: data,
                form: form,
                cb: cb
            });

            if(this.observer.fireEvent('beforecall', this, t) !== false){
                RPC.addTransaction(t);
                this.queueTransaction(t);
                this.observer.fireEvent('call', this, t);
            }
        },
        createMethod : function(c, m){
            var f = function(){
                this.doCall(c, m, Array.prototype.slice.call(arguments, 0));
            }.bind(this);
            f.directCfg = {
                action: c,
                method: m
            };
            return f;
        },

        getTransaction: function(opt){
            return opt && opt.tid ? RPC.getTransaction(opt.tid) : null;
        },

        doCallback: function(t, e){
            var fn = e.status ? 'success' : 'failure';

            if(t && t.cb){
                var hs = t.cb,
                    result = typeof(e.result) !== 'undefined' ? e.result : e.data;
                if(typeof(hs) === 'function' && e.status){
                    hs(result, e);
                } else{
                    hs[fn] && hs[fn].apply(hs.scope, [result, e]);
                }
            }
        }
    });

    return RPC;

})(jQuery, djangoRPC.utils);


// Sets up default jQuery xhr transport if jQuery is present
if (typeof(jQuery) !== 'undefined')
{
    djangoRPC.RPC.transport = function(provider, transaction, data, completeCallback){
        jQuery.ajax({
            url: provider.url,
            ts: transaction,
            type: 'POST',
            timeout: provider.timeout,
            data: data,
            dataType: 'json',
            contentType: 'application/json',
            processData: false,
            complete: completeCallback
        });
    };
}
